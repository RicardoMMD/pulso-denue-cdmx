-- Censos Económicos 2024, CDMX (año de referencia 2023, SCIAN 2023). Una fila por alcaldía × actividad × estrato.
-- Las columnas económicas conservan los códigos de INEGI (ver core.dim_ce_variable). Celdas vacías = confidencial.
-- Sin alcaldía: total de la entidad. Sin actividad: total de todas las actividades. Sin estrato: suma de estratos.

with fuente as (
    select * from {{ source('raw', 'ce2024_cdmx') }}
),

tipado as (
    select
        nullif(trim(e03), '')                        as cve_entidad,
        nullif(trim(e04), '')                        as cve_municipio,
        nullif(trim(sector), '')                     as cve_sector,
        nullif(trim(subsector), '')                  as cve_subsector,
        nullif(trim(rama), '')                       as cve_rama,
        nullif(trim(subrama), '')                    as cve_subrama,
        nullif(trim(clase), '')                      as cve_clase,
        nullif(trim(id_estrato), '')::int            as id_estrato_ce,
        case when trim(codigo) = 'TOTAL DE SECTOR' then null else trim(codigo) end as codigo_actividad,
        nullif(ue, '')::numeric as ue,
        nullif(h001a, '')::numeric as h001a,
        nullif(h000a, '')::numeric as h000a,
        nullif(h010a, '')::numeric as h010a,
        nullif(h020a, '')::numeric as h020a,
        nullif(i000a, '')::numeric as i000a,
        nullif(j000a, '')::numeric as j000a,
        nullif(k000a, '')::numeric as k000a,
        nullif(m000a, '')::numeric as m000a,
        nullif(a111a, '')::numeric as a111a,
        nullif(a121a, '')::numeric as a121a,
        nullif(a131a, '')::numeric as a131a,
        nullif(a211a, '')::numeric as a211a,
        nullif(a221a, '')::numeric as a221a,
        nullif(p000c, '')::numeric as p000c,
        nullif(q000a, '')::numeric as q000a,
        nullif(q000b, '')::numeric as q000b,
        nullif(a700a, '')::numeric as a700a,
        nullif(a800a, '')::numeric as a800a,
        nullif(q000c, '')::numeric as q000c,
        nullif(q000d, '')::numeric as q000d,
        nullif(p000a, '')::numeric as p000a,
        nullif(p000b, '')::numeric as p000b,
        nullif(o010a, '')::numeric as o010a,
        nullif(o020a, '')::numeric as o020a,
        nullif(m700a, '')::numeric as m700a,
        nullif(p030c, '')::numeric as p030c,
        nullif(a511a, '')::numeric as a511a,
        nullif(m020a, '')::numeric as m020a,
        nullif(m050a, '')::numeric as m050a,
        nullif(m091a, '')::numeric as m091a,
        nullif(h001b, '')::numeric as h001b,
        nullif(h001c, '')::numeric as h001c,
        nullif(h001d, '')::numeric as h001d,
        nullif(h000b, '')::numeric as h000b,
        nullif(h000c, '')::numeric as h000c,
        nullif(h000d, '')::numeric as h000d,
        nullif(h010b, '')::numeric as h010b,
        nullif(h010c, '')::numeric as h010c,
        nullif(h010d, '')::numeric as h010d,
        nullif(h101a, '')::numeric as h101a,
        nullif(h101b, '')::numeric as h101b,
        nullif(h101c, '')::numeric as h101c,
        nullif(h101d, '')::numeric as h101d,
        nullif(h203a, '')::numeric as h203a,
        nullif(h203b, '')::numeric as h203b,
        nullif(h203c, '')::numeric as h203c,
        nullif(h203d, '')::numeric as h203d,
        nullif(h020b, '')::numeric as h020b,
        nullif(h020c, '')::numeric as h020c,
        nullif(h020d, '')::numeric as h020d,
        nullif(i000b, '')::numeric as i000b,
        nullif(i000c, '')::numeric as i000c,
        nullif(i000d, '')::numeric as i000d,
        nullif(i100a, '')::numeric as i100a,
        nullif(i100b, '')::numeric as i100b,
        nullif(i100c, '')::numeric as i100c,
        nullif(i100d, '')::numeric as i100d,
        nullif(i200a, '')::numeric as i200a,
        nullif(i200b, '')::numeric as i200b,
        nullif(i200c, '')::numeric as i200c,
        nullif(i200d, '')::numeric as i200d,
        nullif(j010a, '')::numeric as j010a,
        nullif(j203a, '')::numeric as j203a,
        nullif(j300a, '')::numeric as j300a,
        nullif(j400a, '')::numeric as j400a,
        nullif(j500a, '')::numeric as j500a,
        nullif(j600a, '')::numeric as j600a,
        nullif(k010a, '')::numeric as k010a,
        nullif(k020a, '')::numeric as k020a,
        nullif(k030a, '')::numeric as k030a,
        nullif(k311a, '')::numeric as k311a,
        nullif(k042a, '')::numeric as k042a,
        nullif(k412a, '')::numeric as k412a,
        nullif(k050a, '')::numeric as k050a,
        nullif(k610a, '')::numeric as k610a,
        nullif(k620a, '')::numeric as k620a,
        nullif(k060a, '')::numeric as k060a,
        nullif(k070a, '')::numeric as k070a,
        nullif(k810a, '')::numeric as k810a,
        nullif(k820a, '')::numeric as k820a,
        nullif(k910a, '')::numeric as k910a,
        nullif(k950a, '')::numeric as k950a,
        nullif(k096a, '')::numeric as k096a,
        nullif(k976a, '')::numeric as k976a,
        nullif(k090a, '')::numeric as k090a,
        nullif(m010a, '')::numeric as m010a,
        nullif(m030a, '')::numeric as m030a,
        nullif(m090a, '')::numeric as m090a,
        nullif(p100a, '')::numeric as p100a,
        nullif(p100b, '')::numeric as p100b,
        nullif(p030a, '')::numeric as p030a,
        nullif(p030b, '')::numeric as p030b,
        nullif(q010a, '')::numeric as q010a,
        nullif(q020a, '')::numeric as q020a,
        nullif(q030a, '')::numeric as q030a,
        nullif(q400a, '')::numeric as q400a,
        nullif(q900a, '')::numeric as q900a
    from fuente
)

select
    *,
    case
        when cve_clase is not null then 'clase'
        when cve_subrama is not null then 'subrama'
        when cve_rama is not null then 'rama'
        when cve_subsector is not null then 'subsector'
        when cve_sector is not null then 'sector'
        else 'total'
    end                                              as nivel_actividad,
    case
        when cve_municipio is null then 'entidad'
        else 'alcaldia'
    end                                              as nivel_territorial,
    case
        when id_estrato_ce is null then 'suma'
        when id_estrato_ce = 99 then 'confidencial'
        else 'rango'
    end                                              as tipo_estrato
from tipado
