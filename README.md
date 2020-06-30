# Party Jams Dot Biz

Novelty website / app. You type in a word or phrase, a song file is generated with a robot voice that sings it in rhythm.

Either:
- Just ask for a word, make a song based on the word
- Expose the entire composition API


### Design

1. User inputs text + selects a song + options (ie HAM horn level)
1. Sound file is generated and uploaded to cloud storage. File reference is a hash of text + song selection + options (maybe with a retention policy, delete after 30 days or something).
1. Song is exposed, maybe with some front end animations


### Future

1. Greeting cards? Event invite? Even just making calendar integration easy would be an improvement over some sites.

### TODO

1. Amplitude is too complicated, just do this tutorial:
	https://aws.amazon.com/getting-started/hands-on/build-serverless-web-app-lambda-apigateway-s3-dynamodb-cognito/module-4/
	just hash the params and use that to fetch the song	

1. Spin up full API:
	1. Create song
	1. Retrieve song

1. Spin up a simple website. Ensure that it dynamically scales.
	1. AWS amplify probably with rest endpoints. unicorn rides tutorial pretty close

### DONE
1. POC script that works on OSX

1. Figure out how to generate sound file in cloud. Probably dockerized. More difficult than local because of sound card interactions.
	1. https://github.com/serverlesspub/ffmpeg-aws-lambda-layer
	1. https://stackoverflow.com/questions/7629873/how-do-i-mix-audio-files-using-python

