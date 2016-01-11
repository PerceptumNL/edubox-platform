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
                [
                    {
                        "id": "24",
                        "title": "Engels-5",
                        "apps":
                            [
                                {
                                    "id": "7",
                                    "name": "LeestMeer",
                                    "desc": "De LeestMeer applicatie",
                                    "icon": "leestmeer.png",
                                    "path": ["HAVO-5"],
                                },
                                {
                                    "id": "9",
                                    "name": "Duolingo",
                                    "desc": "De Engels-talige Duolingo applicatie",
                                    "icon": "duolingo-en.png",
                                    "path": ["HAVO-5"]
                                }
                            ]
                    },
                    {
                        "id": "13",
                        "title": "Frans-4",
                        "apps":
                            [
                                {
                                    "id": "7",
                                    "name": "LeestMeer",
                                    "desc": "De LeestMeer applicatie",
                                    "icon": "leestmeer.png",
                                    "path": ["HAVO-4"]
                                }
                            ]
                }
        }
    
    :reqheader Authorization: Required OAuth token to authenticate
    
    :statuscode 200: No error
    :statuscode 401: No authenticated user


Event Store API
===============

.. http:get:: /api/events/

    A list of all event store records matching the provided filter parameters.

    **Example request**

    .. sourcecode:: http

        GET /api/events/ HTTP/1.1
        Host: platform.eduraam.nl
        Authorization:

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: text/javascript

        [
            {
                "user": "tim", 
                "app": "LeestMeer",
                "group": "Perceptum", 
                "verb": "http://id.tincanapi.com/verb/viewed", 
                "obj": "http://leestmeer.nl/articles/1", 
                "date": "Jan. 11, 2016, 6:07 p.m."
            }
        ]
    
    :query verb: IRI of the verb to filter on
    :query user: Username of the user to filter on
    :query group: Name of the group to filter on
    :query app: Name of the app to filter on
    :query before: Datetime before which to filter, 
    :query after: Datetime after which to filter, formated as ISO 8601
    :query detail: One of 'simple', 'full'. Default is full

    :reqheader Authorization: required OAuth token to authenticate
    
    :statuscode 200: No error
    :statuscode 400: Verb does not exist or incorrect datetime format provided

    :>jsonarr string user: Username of the user who completed the event
    :>jsonarr string app: The name of the app in which the event was completed.
    :>jsonarr string group: Name of the group the user was signed in with
    :>jsonarr string verb: The IRI of the verb of the event.
    :>jsonarr string obj: The IRI of the object of the event.
    :>jsonarr string date: The datetime of the event, formated as ISO 8601.

.. http:post:: /api/events/

    Post a single or list of new event(s) to the LRS

    **Example request**

    .. sourcecode:: http

        POST /api/events/ HTTP/1.1
        Host: platform.eduraam.nl
        app-token: 0123456789ABCDEF
        Content-Type: text/javascript

        [
            {
                "verb": "http://id.tincanapi.com/verb/viewed",
                "obj": "http://platform.leestmeer.nl/articles/42"
            }

        ]

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK

    :query app-token: The app token describing the context of the event(s). 
        Required. See the section below for explanation.
    :<jsonarr string verb: The IRI of the verb of the event. Required.
    :<jsonarr string obj: The IRI of the object of the event. Required.

    :<jsonarr string timestamp: The datetime of the event, formated as ISO 8601.
        Default is time of posting.
    :<jsonarr string result: The result of the event, meaning depends on the 
        specific verb. Default is None.

    :statuscode 200: No error
    :statuscode 400: Incorrectly formatted token, incorrectly formated post 
        body or referenced body elements do not exists.

The app token
^^^^^^^^^^^^^
This token is generated by the platform and provided to the app when a user 
launches the app. The token is added to the request as a query parameter called 
`token`. This token represents the current user in that app. The token can be
used to identify this combination to the plaform, for instance when sending 
events to the LRS.


The Event verb classes
^^^^^^^^^^^^^^^^^^^^^^
For each verb, a seperate model exists. This means only the verbs listed below
can be used when adding events to the LRS. New verbs can be created on request.

.. class:: ReadEvent(user, app, group, timestamp, article)

Verb IRI
    http://id.tincanapi.com/verb/viewed

Verb Object
    `article`; the article the user read 

Verb Result
    `None`


.. class:: RatedEvent(user, app, group, timestamp, article, rating)

Verb IRI
    http://id.tincanapi.com/verb/rated

Verb Object
    `article`; the article read 

Verb Result
    `rating`; the rating the user gave the article


.. class:: ScoredEvent(user, app, group, timestamp, article, rating)

Verb IRI
    http://adlnet.gov/expapi/verbs/scored

Verb Object
    `article`; the article read 

Verb Result
    `rating`; the difficulty score the user gave the article


.. class:: ClickedEvent(user, app, group, timestamp, article, word)

Verb IRI
    http://adlnet.gov/expapi/verbs/interacted

Verb Object
    `article`; the article read 

Verb Result
    `word`;the word the user clicked in the article

