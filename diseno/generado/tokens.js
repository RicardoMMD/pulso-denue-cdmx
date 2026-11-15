// Generado por diseno/generar.mjs desde diseno/tokens.json. No se edita a mano.
export const version = 1;
export const estado = "elegido por Ricardo el 15 nov 2026 en el laboratorio: paleta vívida, brillo por posprocesado; mapeo de tonos y tipografía pendientes de confirmar en el laboratorio";
export const paletaActiva = "vivida";
/** Macrosectores de la paleta activa, en el orden de ref_macrosector (el índice + 1 es el macrosector del paquete de puntos). */
export const macrosectores = [
  {
    "clave": "comercio",
    "nombre": "Comercio",
    "oscuro": {
      "hex": "#5d7295",
      "rgb": [
        0.3647,
        0.4471,
        0.5843
      ],
      "oklch": {
        "l": 0.55,
        "c": 0.06,
        "h": 260
      }
    },
    "claro": {
      "hex": "#5d7295",
      "contraste": 4.63,
      "oklch": {
        "l": 0.55,
        "c": 0.06,
        "h": 260
      }
    }
  },
  {
    "clave": "alimentos_hospedaje",
    "nombre": "Alimentos y hospedaje",
    "oscuro": {
      "hex": "#ffbd4a",
      "rgb": [
        1,
        0.7412,
        0.2902
      ],
      "oklch": {
        "l": 0.84,
        "c": 0.148,
        "h": 78
      }
    },
    "claro": {
      "hex": "#be8400",
      "contraste": 3.07,
      "oklch": {
        "l": 0.655,
        "c": 0.1365,
        "h": 78
      }
    }
  },
  {
    "clave": "servicios_personales",
    "nombre": "Servicios personales y comunitarios",
    "oscuro": {
      "hex": "#ff6f7a",
      "rgb": [
        1,
        0.4353,
        0.4784
      ],
      "oklch": {
        "l": 0.72,
        "c": 0.1754,
        "h": 18
      }
    },
    "claro": {
      "hex": "#ff5065",
      "contraste": 3.03,
      "oklch": {
        "l": 0.68,
        "c": 0.2099,
        "h": 18
      }
    }
  },
  {
    "clave": "salud_educacion_gobierno",
    "nombre": "Salud, educación y gobierno",
    "oscuro": {
      "hex": "#00d8d9",
      "rgb": [
        0,
        0.8471,
        0.851
      ],
      "oklch": {
        "l": 0.8,
        "c": 0.1365,
        "h": 195
      }
    },
    "claro": {
      "hex": "#00a0a1",
      "contraste": 3.05,
      "oklch": {
        "l": 0.64,
        "c": 0.1092,
        "h": 195
      }
    }
  },
  {
    "clave": "servicios_profesionales",
    "nombre": "Servicios profesionales y financieros",
    "oscuro": {
      "hex": "#a37aff",
      "rgb": [
        0.6392,
        0.4784,
        1
      ],
      "oklch": {
        "l": 0.68,
        "c": 0.19,
        "h": 295
      }
    },
    "claro": {
      "hex": "#a075ff",
      "contraste": 3.08,
      "oklch": {
        "l": 0.67,
        "c": 0.1967,
        "h": 295
      }
    }
  },
  {
    "clave": "industria_construccion",
    "nombre": "Industria y construcción",
    "oscuro": {
      "hex": "#f87103",
      "rgb": [
        0.9725,
        0.4431,
        0.0118
      ],
      "oklch": {
        "l": 0.7,
        "c": 0.19,
        "h": 48
      }
    },
    "claro": {
      "hex": "#eb6a00",
      "contraste": 3.02,
      "oklch": {
        "l": 0.67,
        "c": 0.1825,
        "h": 48
      }
    }
  },
  {
    "clave": "transporte_campo",
    "nombre": "Transporte y campo",
    "oscuro": {
      "hex": "#acf93f",
      "rgb": [
        0.6745,
        0.9765,
        0.2471
      ],
      "oklch": {
        "l": 0.9,
        "c": 0.22,
        "h": 130
      }
    },
    "claro": {
      "hex": "#689f00",
      "contraste": 3.05,
      "oklch": {
        "l": 0.64,
        "c": 0.1722,
        "h": 130
      }
    }
  }
];
/** Todas las paletas candidatas, con la misma forma. */
export const paletas = {
  "sobria": {
    "descripcion": "Comercio apagado y acero; el resto, tonos medios. La más tranquila.",
    "macrosectores": [
      {
        "clave": "comercio",
        "nombre": "Comercio",
        "oscuro": {
          "hex": "#6c839b",
          "rgb": [
            0.4235,
            0.5137,
            0.6078
          ],
          "oklch": {
            "l": 0.6,
            "c": 0.045,
            "h": 250
          }
        },
        "claro": {
          "hex": "#6c839b",
          "contraste": 3.72,
          "oklch": {
            "l": 0.6,
            "c": 0.045,
            "h": 250
          }
        }
      },
      {
        "clave": "alimentos_hospedaje",
        "nombre": "Alimentos y hospedaje",
        "oscuro": {
          "hex": "#fcb442",
          "rgb": [
            0.9882,
            0.7059,
            0.2588
          ],
          "oklch": {
            "l": 0.82,
            "c": 0.15,
            "h": 75
          }
        },
        "claro": {
          "hex": "#c18200",
          "contraste": 3.09,
          "oklch": {
            "l": 0.655,
            "c": 0.1382,
            "h": 75
          }
        }
      },
      {
        "clave": "servicios_personales",
        "nombre": "Servicios personales y comunitarios",
        "oscuro": {
          "hex": "#fc7b9b",
          "rgb": [
            0.9882,
            0.4824,
            0.6078
          ],
          "oklch": {
            "l": 0.74,
            "c": 0.16,
            "h": 6
          }
        },
        "claro": {
          "hex": "#e56688",
          "contraste": 3.03,
          "oklch": {
            "l": 0.675,
            "c": 0.16,
            "h": 6
          }
        }
      },
      {
        "clave": "salud_educacion_gobierno",
        "nombre": "Salud, educación y gobierno",
        "oscuro": {
          "hex": "#47d6cf",
          "rgb": [
            0.2784,
            0.8392,
            0.8118
          ],
          "oklch": {
            "l": 0.8,
            "c": 0.12,
            "h": 190
          }
        },
        "claro": {
          "hex": "#00a19b",
          "contraste": 3.04,
          "oklch": {
            "l": 0.64,
            "c": 0.1105,
            "h": 190
          }
        }
      },
      {
        "clave": "servicios_profesionales",
        "nombre": "Servicios profesionales y financieros",
        "oscuro": {
          "hex": "#ac8ff8",
          "rgb": [
            0.6745,
            0.5608,
            0.9725
          ],
          "oklch": {
            "l": 0.72,
            "c": 0.15,
            "h": 295
          }
        },
        "claro": {
          "hex": "#9b7ee5",
          "contraste": 3.06,
          "oklch": {
            "l": 0.665,
            "c": 0.15,
            "h": 295
          }
        }
      },
      {
        "clave": "industria_construccion",
        "nombre": "Industria y construcción",
        "oscuro": {
          "hex": "#e97c48",
          "rgb": [
            0.9137,
            0.4863,
            0.2824
          ],
          "oklch": {
            "l": 0.7,
            "c": 0.15,
            "h": 45
          }
        },
        "claro": {
          "hex": "#dd713c",
          "contraste": 3.07,
          "oklch": {
            "l": 0.665,
            "c": 0.15,
            "h": 45
          }
        }
      },
      {
        "clave": "transporte_campo",
        "nombre": "Transporte y campo",
        "oscuro": {
          "hex": "#b3ee55",
          "rgb": [
            0.702,
            0.9333,
            0.3333
          ],
          "oklch": {
            "l": 0.88,
            "c": 0.19,
            "h": 128
          }
        },
        "claro": {
          "hex": "#6e9e00",
          "contraste": 3.04,
          "oklch": {
            "l": 0.64,
            "c": 0.1673,
            "h": 128
          }
        }
      }
    ]
  },
  "vivida": {
    "descripcion": "Mismos tonos con más saturación; Comercio sigue apagado. La más llamativa.",
    "macrosectores": [
      {
        "clave": "comercio",
        "nombre": "Comercio",
        "oscuro": {
          "hex": "#5d7295",
          "rgb": [
            0.3647,
            0.4471,
            0.5843
          ],
          "oklch": {
            "l": 0.55,
            "c": 0.06,
            "h": 260
          }
        },
        "claro": {
          "hex": "#5d7295",
          "contraste": 4.63,
          "oklch": {
            "l": 0.55,
            "c": 0.06,
            "h": 260
          }
        }
      },
      {
        "clave": "alimentos_hospedaje",
        "nombre": "Alimentos y hospedaje",
        "oscuro": {
          "hex": "#ffbd4a",
          "rgb": [
            1,
            0.7412,
            0.2902
          ],
          "oklch": {
            "l": 0.84,
            "c": 0.148,
            "h": 78
          }
        },
        "claro": {
          "hex": "#be8400",
          "contraste": 3.07,
          "oklch": {
            "l": 0.655,
            "c": 0.1365,
            "h": 78
          }
        }
      },
      {
        "clave": "servicios_personales",
        "nombre": "Servicios personales y comunitarios",
        "oscuro": {
          "hex": "#ff6f7a",
          "rgb": [
            1,
            0.4353,
            0.4784
          ],
          "oklch": {
            "l": 0.72,
            "c": 0.1754,
            "h": 18
          }
        },
        "claro": {
          "hex": "#ff5065",
          "contraste": 3.03,
          "oklch": {
            "l": 0.68,
            "c": 0.2099,
            "h": 18
          }
        }
      },
      {
        "clave": "salud_educacion_gobierno",
        "nombre": "Salud, educación y gobierno",
        "oscuro": {
          "hex": "#00d8d9",
          "rgb": [
            0,
            0.8471,
            0.851
          ],
          "oklch": {
            "l": 0.8,
            "c": 0.1365,
            "h": 195
          }
        },
        "claro": {
          "hex": "#00a0a1",
          "contraste": 3.05,
          "oklch": {
            "l": 0.64,
            "c": 0.1092,
            "h": 195
          }
        }
      },
      {
        "clave": "servicios_profesionales",
        "nombre": "Servicios profesionales y financieros",
        "oscuro": {
          "hex": "#a37aff",
          "rgb": [
            0.6392,
            0.4784,
            1
          ],
          "oklch": {
            "l": 0.68,
            "c": 0.19,
            "h": 295
          }
        },
        "claro": {
          "hex": "#a075ff",
          "contraste": 3.08,
          "oklch": {
            "l": 0.67,
            "c": 0.1967,
            "h": 295
          }
        }
      },
      {
        "clave": "industria_construccion",
        "nombre": "Industria y construcción",
        "oscuro": {
          "hex": "#f87103",
          "rgb": [
            0.9725,
            0.4431,
            0.0118
          ],
          "oklch": {
            "l": 0.7,
            "c": 0.19,
            "h": 48
          }
        },
        "claro": {
          "hex": "#eb6a00",
          "contraste": 3.02,
          "oklch": {
            "l": 0.67,
            "c": 0.1825,
            "h": 48
          }
        }
      },
      {
        "clave": "transporte_campo",
        "nombre": "Transporte y campo",
        "oscuro": {
          "hex": "#acf93f",
          "rgb": [
            0.6745,
            0.9765,
            0.2471
          ],
          "oklch": {
            "l": 0.9,
            "c": 0.22,
            "h": 130
          }
        },
        "claro": {
          "hex": "#689f00",
          "contraste": 3.05,
          "oklch": {
            "l": 0.64,
            "c": 0.1722,
            "h": 130
          }
        }
      }
    ]
  },
  "fria": {
    "descripcion": "Base de azules, verdes y violetas; los cálidos quedan para los macrosectores chicos.",
    "macrosectores": [
      {
        "clave": "comercio",
        "nombre": "Comercio",
        "oscuro": {
          "hex": "#678c9f",
          "rgb": [
            0.4039,
            0.549,
            0.6235
          ],
          "oklch": {
            "l": 0.62,
            "c": 0.05,
            "h": 230
          }
        },
        "claro": {
          "hex": "#678c9f",
          "contraste": 3.42,
          "oklch": {
            "l": 0.62,
            "c": 0.05,
            "h": 230
          }
        }
      },
      {
        "clave": "alimentos_hospedaje",
        "nombre": "Alimentos y hospedaje",
        "oscuro": {
          "hex": "#f0c12a",
          "rgb": [
            0.9412,
            0.7569,
            0.1647
          ],
          "oklch": {
            "l": 0.83,
            "c": 0.16,
            "h": 90
          }
        },
        "claro": {
          "hex": "#b08c00",
          "contraste": 3.02,
          "oklch": {
            "l": 0.655,
            "c": 0.1339,
            "h": 90
          }
        }
      },
      {
        "clave": "servicios_personales",
        "nombre": "Servicios personales y comunitarios",
        "oscuro": {
          "hex": "#e488be",
          "rgb": [
            0.8941,
            0.5333,
            0.7451
          ],
          "oklch": {
            "l": 0.74,
            "c": 0.13,
            "h": 345
          }
        },
        "claro": {
          "hex": "#cd72a7",
          "contraste": 3.04,
          "oklch": {
            "l": 0.67,
            "c": 0.13,
            "h": 345
          }
        }
      },
      {
        "clave": "salud_educacion_gobierno",
        "nombre": "Salud, educación y gobierno",
        "oscuro": {
          "hex": "#3fd1d9",
          "rgb": [
            0.2471,
            0.8196,
            0.851
          ],
          "oklch": {
            "l": 0.79,
            "c": 0.12,
            "h": 200
          }
        },
        "claro": {
          "hex": "#00a0a6",
          "contraste": 3.03,
          "oklch": {
            "l": 0.64,
            "c": 0.1088,
            "h": 200
          }
        }
      },
      {
        "clave": "servicios_profesionales",
        "nombre": "Servicios profesionales y financieros",
        "oscuro": {
          "hex": "#8494fa",
          "rgb": [
            0.5176,
            0.5804,
            0.9804
          ],
          "oklch": {
            "l": 0.7,
            "c": 0.15,
            "h": 275
          }
        },
        "claro": {
          "hex": "#7988ed",
          "contraste": 3.04,
          "oklch": {
            "l": 0.66,
            "c": 0.15,
            "h": 275
          }
        }
      },
      {
        "clave": "industria_construccion",
        "nombre": "Industria y construcción",
        "oscuro": {
          "hex": "#5bbd74",
          "rgb": [
            0.3569,
            0.7412,
            0.4549
          ],
          "oklch": {
            "l": 0.72,
            "c": 0.14,
            "h": 150
          }
        },
        "claro": {
          "hex": "#3ea25b",
          "contraste": 3.06,
          "oklch": {
            "l": 0.635,
            "c": 0.14,
            "h": 150
          }
        }
      },
      {
        "clave": "transporte_campo",
        "nombre": "Transporte y campo",
        "oscuro": {
          "hex": "#ffc299",
          "rgb": [
            1,
            0.7608,
            0.6
          ],
          "oklch": {
            "l": 0.86,
            "c": 0.0883,
            "h": 55
          }
        },
        "claro": {
          "hex": "#de7300",
          "contraste": 3.04,
          "oklch": {
            "l": 0.665,
            "c": 0.1647,
            "h": 55
          }
        }
      }
    ]
  }
};
export const oscuro = {
  "fondo": "#05060b",
  "alcaldia_relleno": "#0a0e1d",
  "alcaldia_trazo": "#1d2a52",
  "texto": "#c9cfe0",
  "texto_tenue": "#6b7390"
};
export const claro = {
  "descripcion": "Solo para la vista exacta 2D y la interfaz. Cada color se deriva del oscuro bajando la luminosidad hasta el contraste mínimo.",
  "papel": "#faf9f6",
  "texto": "#1c2030",
  "texto_tenue": "#5a6178",
  "trazo": "#c9ccd6",
  "contraste_minimo": 3
};
export const luz = {
  "punto_px": 1.6,
  "alfa": 0.55,
  "atenuado": 0.12,
  "brillo": {
    "tipo": "posprocesado",
    "intensidad": 1.1,
    "umbral": 0.12,
    "suavizado": 0.4
  },
  "halo": {
    "tamano": 2.4,
    "intensidad": 0.18
  },
  "mapeo_tonos": "neutral"
};
export const tipografia = {
  "familia": "Inter",
  "pila": "'Inter', system-ui, -apple-system, 'Segoe UI', sans-serif",
  "licencia": "SIL Open Font License 1.1",
  "archivos": {
    "variable": "fuentes/Inter-latin-variable.woff2",
    "etiqueta_3d": "fuentes/Inter-latin-600.woff"
  },
  "cifras": "tabular-nums",
  "pesos": {
    "normal": 400,
    "medio": 500,
    "fuerte": 650
  },
  "escala_px": {
    "etiqueta": 12,
    "texto": 15,
    "texto_panel": 17,
    "titulo_panel": 28,
    "cifra_principal": 56
  }
};
