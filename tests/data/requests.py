import chalice.app as app
import tests.data as data

TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOjIsImlzcyI6Imh0dHBzOi8vZGV2LWFwaWRpc3RyaWJ1Y2lvbi5zYW50aWxsYW5hLmVzL21jcy9tc3VzZXJzL2FwaS9sb2dpbiIsImlhdCI6MTYyOTk3MDY0MCwiZXhwIjoxNjI5OTc0MjQwLCJuYmYiOjE2Mjk5NzA2NDAsImp0aSI6ImxFR1BlQzRXcGJ6RGN1MG0ifQ.HR1jezh25F6NUu3ztfRdNnAOIU6ZHi6XbbxWCDUPV0s"

request_user_id = app.Request(event_dict=data.events.EVENT_GET_USER_BY_ID)