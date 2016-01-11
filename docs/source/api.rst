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



Settings API
============

.. http:get:: /api/settings/(string:setting_code)

    Returns the value(s) for the setting (defined by the `setting_code`) for the
    current context. The context can be provided by a query parameter 
    `app-token`, or by query parameters `user` and `group`; in both cases the
    setting is resolved for the user-group combination. If only the parameter
    `group` is passed, then the setting is value(s) for the group are returned.
    
    If a setting has a default value, then the it will always resolve to a 
    single value. If not, then it will resolve to a list of values (e.g. a list
    of rss-feeds to include in a news feed).


    **Example request**:

    .. sourcecode:: http

        GET /api/settings/language HTTP/1.1
        Host: platform.eduraam.nl
        Authorization:
        app-token: 0123456789ABCDEF

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Type: text/javascript

        {
            "value": "nl"
        }
    
    :query app-token: The app token describing the user-group context for which
        the setting should be returned. Optional, but not including means at 
        least the `group` parameter is required in order to resolve the setting.

    :query group: The group for which this setting should be returned. Optional, 
        but not including it means the `app-token` parameter is required in 
        order to resolve the setting.
    :query user: The user for which this setting should be returned. Optional; 
        however when included does require the `group` parameter in order to be
        correctly resolved.
    
    :query meta: Including this parameter adds `desc` and `single` fields to the
        returned object.
    :query full: Including this parameter adds the `options` field to to the 
        returned object. 
    
    :reqheader Authorization: required OAuth token to authenticate
    
    :statuscode 200: No error
    :statuscode 400: Invalid group-user context or setting does not exist

    :>json value: The value(s) of the setting; a list if the setting resolves 
        to multiple values (only possbile if the setting has no default)
    :>json desc: Desciption of the setting. Requires the `meta` parameter.
    :>json single: A boolean indicating if the setting resolves to a single 
        value (true) or a list of values (false). Requires the `meta` parameter.
    :>json options: In the case of a single value, this is a list of the 
        possible defaults that could be chosen. In the case of a list it
        contains the removed values that can be re-added to the list. Requires 
        the `full` parameter.


.. http:put:: /api/settings/(string:setting_code)/(string:setting_type)/(string:value)

    If the `setting_type` is "option", the `value` is added to the list of 
    setting values for that setting (defined by `setting_code`) in the provided
    context.

    If the `setting_type` is "value", the `value` becomes the default value for
    that setting in the provided context.

    Context can be provided in the same manner as for the `GET`, either using
    the `app-token` parameter or the `group` and `user` parameters.


    :query app-token: The app token describing the user-group context for which
        the setting should be returned. Optional, but not including means at 
        least the `group` parameter is required in order to resolve the setting.

    :query group: The group for which this setting should be returned. Optional, 
        but not including it means the `app-token` parameter is required in 
        order to resolve the setting.
    :query user: The user for which this setting should be returned. Optional; 
        however when included does require the `group` parameter in order to be
        correctly resolved.
    
    :reqheader Authorization: required OAuth token to authenticate
    
    :statuscode 200: No error
    :statuscode 400: Invalid group-user context or setting does not exist

.. http:delete:: /api/settings/(string:setting_code)/(string:setting_type)/(string:value)

    If the `setting_type` is "option", the `value` is removed from the list of 
    setting values for that setting (defined by `setting_code`) in the provided
    context.

    If the `setting_type` is "value", the `value` is removed as default for
    that setting in the provided context.

    Context can be provided in the same manner as for the `GET`, either using
    the `app-token` parameter or the `group` and `user` parameters.

    
    :query app-token: The app token describing the user-group context for which
        the setting should be returned. Optional, but not including means at 
        least the `group` parameter is required in order to resolve the setting.

    :query group: The group for which this setting should be returned. Optional, 
        but not including it means the `app-token` parameter is required in 
        order to resolve the setting.
    :query user: The user for which this setting should be returned. Optional; 
        however when included does require the `group` parameter in order to be
        correctly resolved.
    
    :reqheader Authorization: required OAuth token to authenticate
    
    :statuscode 200: No error
    :statuscode 400: Invalid group-user context or setting does not exist

