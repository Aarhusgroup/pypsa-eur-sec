
import logging
logger = logging.getLogger(__name__)

#https://stackoverflow.com/questions/20833344/fix-invalid-polygon-in-shapely
#https://stackoverflow.com/questions/13062334/polygon-intersection-error-in-shapely-shapely-geos-topologicalerror-the-opera
#https://shapely.readthedocs.io/en/latest/manual.html#object.buffer
def clean_invalid_geometries(geometries):
    """Fix self-touching or self-crossing polygons; these seem to appear
due to numerical problems from writing and reading, since the geometries
are valid before being written in pypsa-eur/scripts/cluster_network.py"""
    for i,p in geometries.items():
        if not p.is_valid:
            logger.warning(f'Clustered region {i} had an invalid geometry, fixing using zero buffer.')
            geometries[i] = p.buffer(0)



def get_country_emis(network):

    query_string = lambda x : f'bus0 == "{x}" | bus1 == "{x}" | bus2 == "{x}" | bus3 == "{x}" | bus4 == "{x}"'
    id_co2_links = network.links.query(query_string('co2 atmosphere')).index

    country_codes = network.links.loc[id_co2_links].location.unique()
    country_emis = {code:0 for code in country_codes}

    for country in country_codes:
        idx = network.links.query(f'location == "{country}"').index
        id0 = (network.links.loc[idx] == 'co2 atmosphere')['bus0']
        country_emis[country] -= network.links_t.p0[idx[id0]].sum().sum()
        id1 = (network.links.loc[idx] == 'co2 atmosphere')['bus1']
        country_emis[country] -= network.links_t.p1[idx[id1]].sum().sum()
        id2 = (network.links.loc[idx] == 'co2 atmosphere')['bus2']
        country_emis[country] -= network.links_t.p2[idx[id2]].sum().sum()
        id3 = (network.links.loc[idx] == 'co2 atmosphere')['bus3']
        country_emis[country] -= network.links_t.p3[idx[id3]].sum().sum()
        id4 = (network.links.loc[idx] == 'co2 atmosphere')['bus4']
        country_emis[country] -= network.links_t.p4[idx[id4]].sum().sum()

        if country == 'EU':
            id_load_co2 = network.loads.query('bus == "co2 atmosphere"').index
            co2_load = network.loads_t.p[id_load_co2].sum().sum()
            country_emis[country] -= co2_load

        total_emis = np.sum(list(country_emis.values())) 
    
    return country_emis