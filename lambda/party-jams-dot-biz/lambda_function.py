import boto3
from pydub import AudioSegment
import hashlib
# hash_object = hashlib.md5(b'Hello World')
import sox
from random import shuffle

bucket = 'party-jams-dot-biz-sounds'
folder = 'words'
tmp_dir = '/tmp'
# tmp_dir = 'log/'
    # tmp_dir = 'log/'

# def lambda_handler2(event, context):
    # engine = pyttsx3.init()
    # engine.save_to_file('Hello World', 'test.mp3')
    # engine.runAndWait()

sample_event =  {
    "lyrics" :
  [
       {"phrase" : "hello", "beat" : "1"},
       {"phrase" : "world", "beat" : "1"},
       {"phrase" : "nice", "beat" : "1"},
       {"phrase" : "to", "beat" : "1/2"},
       {"phrase" : "meet you", "beat" : "9/2"},
  ]
}    

def lambda_handler(event, context):
    print('running lambda')
    polly = boto3.client('polly')
    s3 = boto3.client('s3')

    lyrics = event['lyrics']
    local_files = []
    print("lyrics = " + str(lyrics))
    for lyric in lyrics:
        phrase = lyric['phrase']
        print("forming phrase: " + phrase)
        hex_digest = hashlib.md5(bytes(phrase, 'utf-8')).hexdigest()
        local_file = tmp_dir + '/' + hex_digest + '.mp3'
        local_wav = tmp_dir + '/' + hex_digest + '.wav'
        response = polly.synthesize_speech(VoiceId='Joanna', OutputFormat='mp3', Text = phrase)

        with open(local_file, 'wb') as fout:
            fout.write(response['AudioStream'].read())
        # sound = AudioSegment.from_mp3(local_file)
        # sound.export(local_wav, format="wav")
        key = hex_digest + '.mp3'
        local_files.append(local_file)
        s3.upload_file(local_file, bucket, key)
    shuffle(local_files)
    cbn = sox.Combiner()
    cbn.build(local_files, tmp_dir + '/shuffled.mp3', 'concatenate')
    s3.upload_file(tmp_dir + '/shuffled.mp3', bucket,  'shuffled.mp3')












    # word = 'foo'
    # local_file = tmp_dir + word + '.mp3'
    # key = folder + word + '.mp3'
    # polly = boto3.client('polly')
    # s3 = boto3.client('s3')

    # response = polly.synthesize_speech(VoiceId='Joanna',    
    #             OutputFormat='mp3', 
    #             Text = 'This is a sample text to be synthesized.')

    # response2 = polly.synthesize_speech(VoiceId='Joanna',    
    #             OutputFormat='mp3', 
    #             Text = 'This is a sample text to be synthesized again.')                

    # with open(local_file, 'wb') as fout:
    #     fout.write(response['AudioStream'].read())

    # local_file2 = tmp_dir + 'word2.mp3'
    # with open(local_file2, 'wb') as fout:
    #     fout.write(response2['AudioStream'].read())        

    # sound1 = AudioSegment.from_mp3(local_file)
    # sound2 = AudioSegment.from_mp3(local_file2)
    # output = sound1.overlay(sound2)
    # output.export(tmp_dir + 'combined.mp3')

    # s3.upload_file(tmp_dir + 'combined.mp3', bucket, key)

if __name__ == 'main':
    lambda_handler(sample_event, {})
