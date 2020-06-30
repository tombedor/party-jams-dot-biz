import boto3
import hashlib
import sox

BUCKET = 'party-jams-dot-biz-sounds'
BACKING_TRACK_FOLDER = 'backing_tracks'
TMP_DIR = '/tmp'

SONG = "smooth_jazz_60_bpm.mp3"
BPM = 60
BEAT_LENGTH_SECONDS = BPM / 60

sample_event =  {
    "lyrics" :
  [
       {"phrase" : "hello", "beats" : "1"},
       {"phrase" : "world", "beats" : "1"},
       {"phrase" : "nice", "beats" : "1"},
       {"phrase" : "to", "beats" : "1/2"},
       {"phrase" : "meet you", "beats" : "9/2"},
  ]
}    

def lambda_handler(event, context):
    polly = boto3.client('polly')
    s3 = boto3.client('s3')

    lyrics = event['lyrics']
    local_files = []
    for lyric in lyrics:
        phrase = lyric['phrase']
        hex_digest = hashlib.md5(bytes(phrase, 'utf-8')).hexdigest()
        local_file = TMP_DIR + '/' + hex_digest + '.mp3'

        # First, write basic response to local
        response = polly.synthesize_speech(VoiceId='Joanna', OutputFormat='mp3', Text = phrase)
        with open(local_file, 'wb') as fout:
            fout.write(response['AudioStream'].read())

        # Figure out desired length of clip
        clip_length = sox.file_info.duration(local_file)
        scale_factor = clip_length / (BEAT_LENGTH_SECONDS * lyric['beats'])

        # Resize clip and write
        transformer = sox.Transformer()
        transformer.tempo(scale_factor)

        local_file_scaled = TMP_DIR + '/' + hex_digest + 'scaled' + '.mp3'
        transformer.build(local_file, local_file_scaled)
        local_files.append(local_file_scaled)

    cbn = sox.Combiner()
    cbn.convert(n_channels = 1)
    cbn.build(local_files, TMP_DIR + '/lyrics.mp3', 'concatenate')
    s3.download_file(BUCKET, BACKING_TRACK_FOLDER + '/' + SONG, TMP_DIR + '/' + SONG)

    backing_cbn = sox.Combiner()
    backing_cbn.convert(n_channels = 1)
    backing_cbn.build([TMP_DIR + '/lyrics.mp3', TMP_DIR + '/' + SONG], TMP_DIR + '/final.mp3', 'merge')

    s3.upload_file(TMP_DIR + '/final.mp3', BUCKET, 'final.mp3')
    

    # cbn.build([TMP_DIR + '/lyrics.mp3', BUCKET + )
    
    # s3.upload_file(TMP_DIR + '/shuffled.mp3', BUCKET,  'shuffled.mp3')












    # word = 'foo'
    # local_file = TMP_DIR + word + '.mp3'
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

    # local_file2 = TMP_DIR + 'word2.mp3'
    # with open(local_file2, 'wb') as fout:
    #     fout.write(response2['AudioStream'].read())        

    # sound1 = AudioSegment.from_mp3(local_file)
    # sound2 = AudioSegment.from_mp3(local_file2)
    # output = sound1.overlay(sound2)
    # output.export(TMP_DIR + 'combined.mp3')

    # s3.upload_file(TMP_DIR + 'combined.mp3', BUCKET, key)

if __name__ == 'main':
    lambda_handler(sample_event, {})
