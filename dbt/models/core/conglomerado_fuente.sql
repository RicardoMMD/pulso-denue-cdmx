-- Todos los conglomerados candidatos, de todas las fuentes, con su geometría (polígono en UTM 14N).
-- metodo_asignacion: 'campo' = lo declara el DENUE (campo de centro comercial); 'espacial' = el
-- establecimiento cae dentro de la geometría. prioridad: menor número gana para el conglomerado principal.
--
--   1 campo DENUE            lo declara INEGI para cada establecimiento
--   2 padrón de mercados     mercados públicos de datos abiertos CDMX (círculo 1.5 × radio equivalente a la superficie)
--   3 OSM centro comercial / mercado (polígono; los puntos con círculo de 30 m)
--   4 OSM zona comercial     landuse=retail
--   5 tianguis               círculo de 40 m
--   6 mercado sobre ruedas   círculo de 40 m
with campo as (
    select
        'denue:' || tipo_denue || '|' || nombre_norm || '|' || grupo                       as clave_natural,
        case tipo_denue
            when 'MERCADO PUBLICO' then 'mercado público'
            when 'CENTRO Y PLAZA COMERCIAL' then 'centro o plaza comercial'
            when 'EDIFICIO COMERCIAL Y DE SERVICIOS' then 'edificio comercial y de servicios'
            when 'CENTRAL DE ABASTO' then 'central de abasto'
            when 'PASAJE Y ANDADOR COMERCIAL' then 'pasaje o andador comercial'
            when 'HOSPITAL, CENTRO MEDICO O CLINICA' then 'hospital o centro médico'
            when 'TIANGUIS, BAZAR O PULGA' then 'tianguis, bazar o pulga'
            when 'AEROPUERTO' then 'aeropuerto'
            when 'PARQUE RECREATIVO' then 'parque recreativo'
            when 'CENTRAL CAMIONERA' then 'central camionera'
            when 'CORREDORES TURÍSTICOS' then 'corredor turístico'
            when 'ZONA INDUSTRIAL' then 'zona industrial'
            when 'PARQUE INDUSTRIAL' then 'parque industrial'
            when 'CORREDOR INDUSTRIAL' then 'corredor industrial'
            when 'CIUDAD INDUSTRIAL' then 'ciudad industrial'
            when 'HOTELES' then 'hoteles'
            when 'ESCUELAS' then 'escuelas'
            else 'otro conjunto'
        end                                                                                 as tipo,
        case
            when tipo_denue in ('MERCADO PUBLICO', 'CENTRO Y PLAZA COMERCIAL', 'EDIFICIO COMERCIAL Y DE SERVICIOS',
                                'CENTRAL DE ABASTO', 'PASAJE Y ANDADOR COMERCIAL', 'TIANGUIS, BAZAR O PULGA',
                                'OTROS CONJUNTOS COMERCIALES') then 'comercio'
            when tipo_denue in ('ZONA INDUSTRIAL', 'PARQUE INDUSTRIAL', 'CORREDOR INDUSTRIAL', 'CIUDAD INDUSTRIAL') then 'industria'
            when tipo_denue in ('HOSPITAL, CENTRO MEDICO O CLINICA', 'AEROPUERTO', 'CENTRAL CAMIONERA', 'PARQUE RECREATIVO',
                                'CORREDORES TURÍSTICOS', 'HOTELES', 'ESCUELAS') then 'servicios y equipamiento'
            else 'otro'
        end                                                                                 as categoria,
        initcap(nombre_norm)                                                                as nombre,
        null::text                                                                          as alcaldia,
        'campo DENUE (centro comercial)'::text                                              as origen,
        'campo'::text                                                                       as metodo_asignacion,
        1                                                                                   as prioridad,
        n_max                                                                               as num_locales,
        geom_utm
    from {{ ref('conglomerado_campo_denue') }}
),

padron as (
    select
        'padron:' || id_mercado, 'mercado público', 'comercio', mercado, alcaldia,
        'padrón de mercados públicos CDMX', 'espacial', 2, num_locales,
        st_buffer(geom_utm, 1.5 * sqrt(superficie_m2 / pi()))
    from {{ ref('stg_mercados') }}
),

osm as (
    select
        'osm:' || osm_tipo || '/' || osm_id,
        case categoria when 'mall' then 'centro comercial (OSM)' when 'marketplace' then 'mercado (OSM)' else 'zona comercial (OSM)' end,
        'comercio',
        coalesce(nombre, 'sin nombre (OSM ' || osm_tipo || ' ' || osm_id || ')'),
        null::text, 'OpenStreetMap', 'espacial',
        case categoria when 'retail' then 4 else 3 end,
        null::int,
        case when es_punto then st_buffer(geom_utm, 30) else geom_utm end
    from {{ ref('stg_osm_comercio') }}
    where categoria in ('mall', 'marketplace', 'retail')
      and (es_punto or st_area(geom_utm) between 100 and 2000000)
),

tianguis as (
    select
        'tianguis:' || id_tianguis, 'tianguis', 'comercio',
        'Tianguis ' || coalesce(ubicacion, colonia) || ' (' || dia || ')', alcaldia,
        'tianguis de datos abiertos CDMX', 'espacial', 5, num_oferentes, st_buffer(geom_utm, 40)
    from {{ ref('stg_tianguis') }}
),

msr as (
    select
        'msr:' || id_msr, 'mercado sobre ruedas', 'comercio',
        'Mercado sobre ruedas ' || ruta || ' (' || coalesce(direccion, colonia) || ')', alcaldia,
        'mercados sobre ruedas de datos abiertos CDMX', 'espacial', 6, num_oferentes, st_buffer(geom_utm, 40)
    from {{ ref('stg_mercados_sobre_ruedas') }}
)

select * from campo
union all select * from padron
union all select * from osm
union all select * from tianguis
union all select * from msr
