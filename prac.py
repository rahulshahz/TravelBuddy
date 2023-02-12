import geocoder
g = geocoder.mapbox('San Francisco, CA', key='pk.eyJ1IjoicmFodWxzaGFoeiIsImEiOiJja3lpbGdnN2ExNWw0MnZwMDhzdTZxa2FwIn0.po1o8LBd0wnNBE6dpr5Ouw')
j=g.json
print(j["lat"])
print(j["lng"])