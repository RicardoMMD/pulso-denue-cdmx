-- Población oficial por alcaldía del Censo 2020 (ITER, fila de total municipal). Fuente de verdad para totales.
select
    mun                                                                    as cve_municipio,
    trim(nom_mun)                                                          as alcaldia,
    pobtot::int                                                            as poblacion,
    case when pob0_14 ~ '^\d+$' then pob0_14::int end                      as poblacion_0_14,
    case when pob65_mas ~ '^\d+$' then pob65_mas::int end                  as poblacion_65_mas,
    case when tothog ~ '^\d+$' then tothog::int end                        as hogares
from {{ source('raw', 'censo2020_iter') }}
where mun <> '000' and loc = '0000'
