#!/usr/bin/env bash
# PreToolUse hook — gate de producción: el agente llega hasta la puerta y no la cruza.
#
# Para comandos Bash que coinciden con un patrón de despliegue, y para herramientas
# MCP cuyo nombre sugiere deploy/release/rollback, pide aprobación humana en ese
# momento (permissionDecision "ask"). El agente no puede concederse esa aprobación.
#
# Patrones: .claude/deploy-patterns (una regex ERE por línea, sin distinguir
# mayúsculas). Si no existe, se usan los de abajo.
# DEPLOY_GATE_MODE=deny (en el entorno de Claude Code) bloquea en vez de preguntar;
# úsalo si trabajas en un modo que no muestra confirmaciones.
set -euo pipefail

input=$(cat)
project="${CLAUDE_PROJECT_DIR:-$(pwd)}"
tool=$(jq -r '.tool_name // empty' <<<"$input")

default_patterns=(
  '\b(deploy|release|promote|ship)\b.*\b(prod|production|prd|live)\b'
  '\b(prod|production|prd)\b.*\b(deploy|release|promote)\b'
  '\b(kubectl|helm)\b.*\bprod'
  '\bterraform\b.*\b(apply|destroy)\b'
  '\b(migrate|upgrade)\b.*\b(prod|production)\b'
  '\bgit[[:space:]]+push\b.*\b(main|master|production|release)\b'
  '\bgit[[:space:]]+push\b.*(--force|-f\b)'
)

decide() {
  if [[ "${DEPLOY_GATE_MODE:-ask}" == "deny" ]]; then
    echo "Bloqueado por el gate de producción: $1. Pide al usuario que lo ejecute o lo autorice." >&2
    exit 2
  fi
  jq -n --arg r "Gate de producción: $1. Requiere tu aprobación explícita." \
    '{hookSpecificOutput: {hookEventName: "PreToolUse",
      permissionDecision: "ask", permissionDecisionReason: $r}}'
  exit 0
}

if [[ "$tool" == mcp__* ]]; then
  if grep -Eiq '(deploy|release|rollback|promote|publish)' <<<"$tool"; then
    decide "la herramienta $tool puede desplegar o revertir"
  fi
  exit 0
fi

[[ "$tool" == "Bash" ]] || exit 0
cmd=$(jq -r '.tool_input.command // empty' <<<"$input")

patterns=()
if [[ -f "$project/.claude/deploy-patterns" ]]; then
  while IFS= read -r p; do
    [[ "$p" =~ ^[[:space:]]*(#|$) ]] || patterns+=("$p")
  done <"$project/.claude/deploy-patterns"
else
  patterns=("${default_patterns[@]}")
fi

for p in "${patterns[@]}"; do
  if grep -Eiq -- "$p" <<<"$cmd"; then
    decide "el comando coincide con /$p/"
  fi
done
exit 0
