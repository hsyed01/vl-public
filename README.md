# Verified Listens

Objective: To develop an API that given a set of optional inputs (podcast show, podcast episode, genre, content duration, etc) as well as the ad placement marker (seconds into a show), the api will respond with the probability of the user listening to said ad.

### Example API Call

```jsx
GET /will-listen-to?feed='https://feeds.megaphone.fm/stuffyoushouldknow'&seconds=600

POST /will-listen-to
{
	"feed": "https://feeds.megaphone.fm/conan-obrien-needs-a-friend",
	"enclosure": "https://feeds.megaphone.fm/episodes/episode-1056-20241128.m4a",
	"seconds": 600,
	"ua": "Google Podcasts/1.0.0.12345 (Linux; U; Android 13; Pixel 7)"
	"state": "Connecticut"
}

Responses
200 0.85 // (the probability score that the user will listen up to the given number of seconds)
400 enclosure or seconds not provided or is malformed
404 enclosure not found
500 server error
```

Note: we do not need to implement both GET and POST. Just pick one for your implementation.

## Model Training

Inputs: We will receive a series of CSVs with each row containing the following data:

- Podcast RSS Feed (aka the show)
- Enclosure URL (aka the episode)
- Persistent User ID (UUID)
- User Agent
- State (US)
- Duration of Listen (seconds)

### Requirements

Given a show that is part of our data set, return the given probability that someone will listen up to a specific timestamp.

There sample data file is in /podcast_engagement_data.csv

Decide which data relationships make the most sense to make the prediction.

## Final Rubric

Your work will be evaluated on the following factors listed in priority order:

- a trained ML model is created
- the ML model returns an output in the form of a percentage value
- an API route that takes the correct inputs
- the API returns appropriate success response
- the API returns other responses

NOTE: It is important to note that the accuracy of the model is NOT the primary concern of this project, though bonus points will be awarded for thoughtful analysis, as long as the primary objectives listed above are met.
