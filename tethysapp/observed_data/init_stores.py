# Put your persistent store initializer functions in here

from .model import engine, SessionMaker, Base, StreamGage

def init_stream_gage_db(first_time):
    """
    An example persistent store initializer function
    """
    # Create tables
    Base.metadata.create_all(engine)

    # Initial data
    if first_time:
        # Make session
        session = SessionMaker()


        # Gage 1
        gage1 = StreamGage(latitude=18.976622,
                           longitude=-71.28982099634956,
                           value=1 name=Presa de Sabaneta)

        session.add(gage1)


        # Gage 2
        gage2 = StreamGage(latitude=19.031064,
                           longitude=-71.29954095389662,
                           value=2 name=Paso de Lima)

        session.add(gage2)


        # Gage 3
        gage3 = StreamGage(latitude=18.892486,
                           longitude=-71.25836565957668,
                           value=3 name=Canafistol)

        session.add(gage3)

        # Gage 4
        gage4 = StreamGage(latitude=18.724674,
                           longitude=-71.10897454764346,
                           value=4 name=Sabana Alta)

        session.add(gage4)

        # Gage 5
        gage5 = StreamGage(latitude=18.817731,
                           longitude=-71.11786344369251,
                           value=5 Name=El Cacheo)

        session.add(gage5)



        session.commit()


