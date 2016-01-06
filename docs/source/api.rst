App List API
============

.. http:get:: /api/apps/

    A listing of all possible contexts for the currently logged-in user

    **Example request**:

    .. sourcecode:: http

        GET /api/apps/ HTTP/1.1
        Host: platform.eduraam.nl
        Authorization:

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: text/javascript

        {
            "groups":
                {
                    "Engels-5":
                        [
                            {
                                "name": "LeestMeer",
                                "icon": "leestmeer.png",
                                "path": ["HAVO-5"],
                                "location": "http://platform.leestmeer.nl",
                                "token": "0123456789ABCDEF"
                            },
                            {
                                "name": "Duolingo",
                                "icon": "duolingo-en.png",
                                "location": "https://www.duolingo.com",
                                "path": ["HAVO-5"]
                                "token": "ABCDEF0123456789"
                            }
                        ],
                    "Frans-4":
                        [
                            {
                                "name": "LeestMeer",
                                "icon": "leestmeer.png",
                                "location": "http://platform.leestmeer.nl",
                                "path": ["HAVO-4"]
                                "token": "FEDCBA9876543210"
                            }
                        ]
                }
        }
    
    :reqheader Authorization: required OAuth token to authenticate
    
    :statuscode 200: no error
    :statuscode 401: no authenticated user


Event Store API
===============

.. module:: kb.events.models

.. class:: ReadEvent(user, app, group, timestamp, article)

.. class:: RatedEvent(user, app, group, timestamp, article, rating)

.. class:: ScoredEvent(user, app, group, timestamp, article, rating)

.. class:: ClickedEvent(user, app, group, timestamp, article, word)

.. module:: kb.events.views

.. automethod:: API.get

.. automethod:: API.post

