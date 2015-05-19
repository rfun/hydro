from tethys_apps.base import TethysAppBase, url_map_maker
from tethys_apps.base import PersistentStore

class ObservedHydrologicData(TethysAppBase):
    """
    Tethys app class for Observed Hydrologic Data.
    """

    name = 'Observed Hydrologic Data'
    index = 'observed_data:home'
    icon = 'observed_data/images/logo.png'
    package = 'observed_data'
    root_url = 'observed-data'
    color = '#e67e22'
        
    def url_maps(self):
        """
        Add controllers
        """
        UrlMap = url_map_maker(self.root_url)

        url_maps = (UrlMap(name='home',
                           url='observed-data',
                           controller='observed_data.controllers.home'),              
                    UrlMap(name='plot',
                           url='observed-data/plot',
                           controller='observed_data.controllers.plot'
                           ),
                     UrlMap(name='displaySites',
                           url='observed-data/displaySites',
                           controller='observed_data.controllers.displaySites'
                           ),
                     UrlMap(name='getSites',
                           url='observed-data/getSites',
                           controller='observed_data.controllers.getSites'
                           ),
                     UrlMap(name='getVariables',
                           url='observed-data/getVariables',
                           controller='observed_data.controllers.getVariables'
                           ),
                     UrlMap(name='addSites',
                           url='observed-data/addsites',
                           controller='observed_data.controllers.siteprocess'
                           )

        )

        return url_maps
    def persistent_stores(self):
        """
        Add one or more persistent stores
        """
        stores = (PersistentStore(name='sites_db',
                                  initializer='init_stores:init_sites_db',
                                  spatial=True
                ),
        )

        return stores





