import json
from loguru import logger
import sys
import datetime

import cv2

from fastapi import APIRouter, File, UploadFile
from fastapi.responses import StreamingResponse

from tempfile import NamedTemporaryFile

from deep_sort_realtime.deepsort_tracker import DeepSort

from io import BytesIO
import os

from helper import create_video_writer
from app import get_model_predict

router = APIRouter(prefix="/tracking", tags=["Tracking"])


@router.post("/deepsort")
def tracking(file: UploadFile = File(...)):
    temp = NamedTemporaryFile(delete=False)
    try:
        try:
            contents = file.file.read()
            with temp as f:
                f.write(contents)
        except Exception:
            return {"message": "There was an error uploading the file"}
        finally:
            file.file.close()

        CONFIDENCE_THRESHOLD = 0.8
        GREEN = (0, 255, 0)
        WHITE = (255, 255, 255)

        # initialize the video capture object
        video_cap = cv2.VideoCapture(temp.name)
        # initialize the video writer object
        writer = create_video_writer(video_cap, "output.mp4")

        # load the pre-trained YOLOv8n model
        model = get_model_predict
        tracker = DeepSort(max_age=50)

        while True:
            start = datetime.datetime.now()

            ret, frame = video_cap.read()

            if not ret:
                break

            # run the YOLO model on the frame
            detections = model(frame)[0]

            # initialize the list of bounding boxes and confidences
            results = []

            # loop over the detections
            for data in detections.boxes.data.tolist():
                # extract the confidence (i.e., probability) associated with the prediction
                confidence = data[4]

                # filter out weak detections by ensuring the
                # confidence is greater than the minimum confidence
                if float(confidence) < CONFIDENCE_THRESHOLD:
                    continue

                # if the confidence is greater than the minimum confidence,
                # get the bounding box and the class id
                xmin, ymin, xmax, ymax = (
                    int(data[0]),
                    int(data[1]),
                    int(data[2]),
                    int(data[3]),
                )
                class_id = int(data[5])
                # add the bounding box (x, y, w, h), confidence and class id to the results list
                results.append(
                    [[xmin, ymin, xmax - xmin, ymax - ymin], confidence, class_id]
                )

            # update the tracker with the new detections
            tracks = tracker.update_tracks(results, frame=frame)
            # loop over the tracks
            for track in tracks:
                # if the track is not confirmed, ignore it
                if not track.is_confirmed():
                    continue

                # get the track id and the bounding box
                track_id = track.track_id
                ltrb = track.to_ltrb()

                xmin, ymin, xmax, ymax = (
                    int(ltrb[0]),
                    int(ltrb[1]),
                    int(ltrb[2]),
                    int(ltrb[3]),
                )
                # draw the bounding box and the track id
                cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), GREEN, 2)
                cv2.rectangle(frame, (xmin, ymin - 20), (xmin + 20, ymin), GREEN, -1)
                cv2.putText(
                    frame,
                    str(track_id),
                    (xmin + 5, ymin - 8),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    WHITE,
                    2,
                )

            # end time to compute the fps
            end = datetime.datetime.now()
            # show the time it took to process 1 frame
            print(
                f"Time to process 1 frame: {(end - start).total_seconds() * 1000:.0f} milliseconds"
            )
            # calculate the frame per second and draw it on the frame
            fps = f"FPS: {1 / (end - start).total_seconds():.2f}"
            cv2.putText(
                frame, fps, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 8
            )

            # show the frame to our screen
            cv2.imshow("Frame", frame)
            writer.write(frame)
            if cv2.waitKey(1) == ord("q"):
                break

        video_cap.release()
        writer.release()
        cv2.destroyAllWindows()
    except Exception:
        return {"message": "There was an error processing the file"}
    finally:
        # temp.close()  # the `with` statement above takes care of closing the file
        os.remove(temp.name)

    return video_cap
