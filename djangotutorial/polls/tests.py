import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Question

def create_question(question_text, days):
    """
    Create question with given text and days posted since NOW
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)

class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
        Test that users can not access details of future questions
        """
        question = create_question(question_target="Future Question", days = 30)
        response = self.client.get(reverse("polls:detail", args=(question.id)))
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        Test users CAN access details about past/current questions
        """
        question = create_question(question_text="Old Question", days = -30)
        response = self.client.get(reverse("polls:detail", args=(question.id)))
        # different ways to test this :
        #   you could also just : assertContains(response, question.question_text)
        self.assertQuerySetEqual(
            response.context["object_list"],
            [question]
        )
    
class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """
        If no question exists, ensure appropriate message is displayed
        """
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code,200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_past_question(self):
        """
        Questions with pub_date in the past are displayed on index page
        """
        question = create_question("Past question", days=-30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question]
        )

    def test_future_question(self):
        """
        Questions with pub_date in the future are NOT displayed on index page
        """
        question = create_question("Future question", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_future_question_and_past_question(self):
        """
        Test interaction with old and future questions. Ensure functionality applies properly
        """
        question1 = create_question("Future question", days=30)
        question2 = create_question("Past question", days=-30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question2]
        )

    def test_two_past_questions(self):
        """
        Ensure index page displays multiple questions (at least 2)
        """
        question1 = create_question("Future question", days=-5)
        question2 = create_question("Past question", days=-30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question1, question2] #order matters here
        )


class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        """
        Make sure future questions do not return true...
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        Make sure returns False for questions older than 1 day
        """
        time = timezone.now() - datetime.timedelta(days=1,seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        Returns True, when question was published within a day
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)

# Create your tests here.
