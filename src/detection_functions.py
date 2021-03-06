import urllib2
import urllib
import unirest
import json
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
register_openers()

api_key = "YOUR_ANIMETRICS_API_KEY"
mashape_key = "YOUR_MASHAPE_KEY"

def detect_faces(image_fname):
   data, headers = multipart_encode({"image": open(image_fname, "rb"), "selector" : "FACE"})
   headers["X-Mashape-Key"] = mashape_key
   request = urllib2.Request("https://animetrics.p.mashape.com/detect?api_key=" + api_key, data, headers)
   response = urllib2.urlopen(request).read()
   return json.loads(response)

def enroll_person(image_fname, person_id):
   faces_data = detect_faces(image_fname)["images"][0]
   if not faces_data["faces"]:
       print "NO FACES DETECTED! Finishing..."
       return
   for face in faces_data["faces"]:
       query_uri = """https://animetrics.p.mashape.com/enroll?
                        api_key=%s&
                        gallery_id=%s&
                        image_id=%s&
                        subject_id=%s&
                        height=%d&
                        width=%d&
                        topLeftX=%d&
                        topLeftY=%d
                        """ % (api_key, "Designers", faces_data["image_id"], person_id,
                               face["height"], face["width"], face["topLeftX"], face["topLeftY"])
       query_uri = query_uri.replace("\t", "").replace(" ", "").replace("\n", "")
       response = unirest.get(query_uri,
         headers={
           "X-Mashape-Key": mashape_key,
           "Accept": "application/json"
         }
       )
       return response.body


def crop(big_image,left,top,height,width,filename):
    from PIL import Image
    im = Image.open(big_image)
    box = (left,top,left + width,top + height)
    region = im.crop(box)
    print "..saving to:", filename
    region.save(filename)

def get_timestamp() :
    import time
    import datetime
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d-%H-%H-%S')
    timestamp = str(st)
    return timestamp

def make_filename(person_name) :
    return  get_timestamp()+ "_" + person_name + ".jpg"

def recognize_and_save_person(image_fname):
   faces_data = detect_faces(image_fname)["images"][0]
   if not faces_data["faces"]:
       print "NO FACES DETECTED! Finishing..."
       return
   for face in faces_data["faces"]:
       query_uri = """https://animetrics.p.mashape.com/recognize?
                        api_key=%s&
                        gallery_id=%s&
                        image_id=%s&
                        height=%d&
                        width=%d&
                        topLeftX=%d&
                        topLeftY=%d
                        """ % (api_key, "Designers", faces_data["image_id"],
                               face["height"], face["width"], face["topLeftX"], face["topLeftY"])
       query_uri = query_uri.replace("\t", "").replace(" ", "").replace("\n", "")
       response = unirest.get(query_uri,
         headers={
           "X-Mashape-Key": mashape_key,
           "Accept": "application/json"
         }
       )
       candidates_probs = response.body["images"][0]["candidates"]
       selected_candidate = max([(prob, cand_name) for cand_name, prob in candidates_probs.items()])[1]
       crop(image_fname, face["topLeftX"], face["topLeftY"], face["height"], face["width"], make_filename(selected_candidate))
       import time
       #to not exceed maximum request frequency
       time.sleep(1)


