# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

import random
import json

QUESTION_LIST = [
                "mathematics",
                "english",
                "commerce",
                "accounting",
                "biology",
                "physics",
                "chemistry",
                "englishlit",
                "government",
                "crk",
                "geography",
                "economics",
                "irk",
                "civiledu",
                "insurance",
                "currentaffairs",
                "history"
            ]

class ActionGetQuestions(Action):

    def name(self) -> Text:
        return "action_get_question"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        subject = tracker.get_slot("subject")

        if subject not in QUESTION_LIST:
            dispatcher.utter_message(text="sorry that subject was not found")
            return []

        result = self.requestJson(subject)

        _, question, _, _, _, answer, *_other = result.values()
        a, b, c, d = result["option"].values()

        chatText = f"""{question}
            A. {a}
            B. {b}
            C. {c}
            D. {d}
        """

        selected_dictA = json.dumps({"selected_answer": "a"})
        selected_dictB = json.dumps({"selected_answer": "b"})
        selected_dictC = json.dumps({"selected_answer": "c"})
        selected_dictD = json.dumps({"selected_answer": "d"})
        intent = "select_answer"
        dispatcher.utter_message(text=chatText, buttons = [
                {"payload": f"/{intent}{selected_dictA}", "title": f" A "},
                {"payload": f"/{intent}{selected_dictB}", "title": f" B "},
                {"payload": f"/{intent}{selected_dictC}", "title": f" C "},
                {"payload": f"/{intent}{selected_dictD}", "title": f" D "}
            ])

        return [SlotSet("slot_question_answer", answer)]

    def requestJson(self, subject="chemistry"):

        with open(f"./data_store/{subject}.json") as json_file: 
            data = json.load(json_file) 

            question_length = len(data["data"]) - 1
            
            random_question_index = random.randint(0, question_length)
            print(data["data"][random_question_index])
            return data["data"][random_question_index]


class ActionDetermineCorrectAnswer(Action):

    def name(self) -> Text:
        return "action_determine_correct_answer"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        selected_answer = tracker.get_slot("selected_answer")
        slot_question_answer = tracker.get_slot("slot_question_answer")
        subject = tracker.get_slot("subject")

        print(f"selected_answer : {selected_answer}")
        print(f"slot_question_answer : {slot_question_answer}")

        chatText = ""
        if selected_answer == slot_question_answer:
            chatText = "Thats the correct answer"
        else:
            chatText = f"The correct answer is {slot_question_answer.capitalize()}." 

        chatText = f"{chatText}\nWould you like another random {subject} question"
        print(chatText)

        subject_entity = json.dumps({"subject": subject})

        dispatcher.utter_message(text=chatText, buttons = [
                {"payload": f"/give_question{subject_entity}", "title": "Yes"},
                {"payload": f"/goodbye", "title": "No"}
            ])

        return [SlotSet("slot_question_answer", slot_question_answer)]

class ActionReturnListOfSubjects(Action):

    def name(self) -> Text:
        return "action_return_list_of_subjects"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        chatText = "I can give questions in the following subjects : \n"

        for i in QUESTION_LIST: 
            chatText += f"* {i} \n"
        dispatcher.utter_message(text=chatText)
        
        return []
