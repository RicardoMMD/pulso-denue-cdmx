-- Limpieza de tipos y texto del DENUE. Una fila por establecimiento y edición.
-- Los textos libres pasan por reparar_texto (mojibake de INEGI: "CARTÃ?N" → "CARTÓN"); texto_danado marca lo que no se pudo reparar.
-- No decide nada de negocio: eso es de core.

with fuente as (
    select * from {{ source('raw', 'denue') }}
),

limpio as (
    select
        edicion,
        id::bigint                                   as id_denue,
        clee,
        nullif({{ reparar_texto('trim(nom_estab)') }}, '')                  as nombre,
        nullif({{ reparar_texto('trim(raz_social)') }}, '')                 as razon_social,
        codigo_act                                   as clase_scian,
        trim(nombre_act)                             as nombre_actividad,
        per_ocu                                      as estrato,
        tipounieco                                   as tipo_unidad,

        nullif(trim(tipo_vial), '')                  as tipo_vialidad,
        nullif({{ reparar_texto('trim(nom_vial)') }}, '')                   as vialidad,
        nullif(trim(tipo_v_e_1), '')                 as tipo_entre_vialidad_1,
        nullif({{ reparar_texto('trim(nom_v_e_1)') }}, '')                  as entre_vialidad_1,
        nullif(trim(tipo_v_e_2), '')                 as tipo_entre_vialidad_2,
        nullif({{ reparar_texto('trim(nom_v_e_2)') }}, '')                  as entre_vialidad_2,
        nullif(trim(tipo_v_e_3), '')                 as tipo_vialidad_posterior,
        nullif({{ reparar_texto('trim(nom_v_e_3)') }}, '')                  as vialidad_posterior,
        nullif(trim(numero_ext), '')                 as numero_exterior,
        nullif(trim(letra_ext), '')                  as letra_exterior,
        nullif({{ reparar_texto('trim(edificio)') }}, '')                   as edificio,
        nullif(trim(edificio_e), '')                 as piso,
        nullif(trim(numero_int), '')                 as numero_interior,
        nullif(trim(letra_int), '')                  as letra_interior,
        nullif(trim(tipo_asent), '')                 as tipo_asentamiento,
        nullif({{ reparar_texto('trim(nomb_asent)') }}, '')                 as colonia,
        nullif(trim(tipocencom), '')                 as tipo_centro_comercial,
        nullif({{ reparar_texto('trim(nom_cencom)') }}, '')                 as centro_comercial,
        nullif(trim(num_local), '')                  as numero_local,
        nullif(trim(cod_postal), '')                 as codigo_postal,

        cve_ent                                      as cve_entidad,
        cve_mun                                      as cve_municipio,
        cve_ent || cve_mun                           as cve_mun_completa,
        trim(municipio)                              as municipio,
        cve_loc                                      as cve_localidad,
        trim(localidad)                              as localidad,
        ageb,
        manzana,
        cve_ent || cve_mun || cve_loc || ageb || manzana as cve_manzana,

        nullif(trim(telefono), '')                   as telefono,
        nullif(trim(correoelec), '')                 as correo,
        nullif(trim(www), '')                        as sitio_web,

        latitud::numeric(10, 8)                      as latitud,
        longitud::numeric(11, 8)                     as longitud,

        -- fecha_alta viene como AAAA-MM; algunas filas traen AAAA MM o AAAA_MM, y 2 filas DD/MM/AAAA
        case
            when trim(fecha_alta) ~ '^\d{4}[-_ ](0[1-9]|1[0-2])$'
                then make_date(left(trim(fecha_alta), 4)::int, substr(trim(fecha_alta), 6, 2)::int, 1)
            when trim(fecha_alta) ~ '^\d{2}/\d{2}/\d{4}$' then to_date(trim(fecha_alta), 'DD/MM/YYYY')
        end                                          as fecha_alta
    from fuente
)

select
    *,
    concat_ws(' ', nombre, razon_social, vialidad, entre_vialidad_1, entre_vialidad_2, vialidad_posterior,
              edificio, colonia, centro_comercial) ~ '{{ patron_mojibake() }}' as texto_danado,
    st_setsrid(st_makepoint(longitud, latitud), 4326)::geometry(point, 4326) as geom,
    -- Algunos puntos caen fuera de la ciudad (error de geocodificación de INEGI)
    (latitud between 19.0 and 19.65 and longitud between -99.40 and -98.90)  as coord_en_cdmx
from limpio
