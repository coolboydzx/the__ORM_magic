# Software Architecture and Design Patterns -- Lab 3 starter code
# An implementation of the Service Layer
# Copyright (C) 2021 Hui Lan


# word and its difficulty level

WORD_DIFFICULTY_LEVEL = {'starbucks': 5, 'luckin': 4, 'secondcup': 4, 'costa': 3, 'timhortons': 3, 'frappuccino': 6}
import model
import orm


class UnknownUser(Exception):
    pass


def is_unknown_user(username, users):
    return username in {b.username for b in users}


def is_unknown_password(password, users):
    return password in {b.password for b in users}


class NoArticleMatched(Exception):
    pass


min = 0
article_id = 0


def is_no_article_matched(Lu, articles):
    global min
    global Article_id
    min = 0
    Article_id = 0
    for La in articles:
        if (La.level > Lu):
            if (min == 0):
                min = La.level
                Article_id = La.article_id
            else:
                if (min > La.level):
                    min = La.level
                    Article_id = La.article_id
    if min == 0:
        return False


def read(user, user_repo, article_repo, session):
    users = user_repo.list()
    if not is_unknown_user(user.username, users):
        raise UnknownUser(f"Unknown user {user.username}")
    if not is_unknown_password(user.password, users):
        raise UnknownUser(f"Unknown password {user.password}")
    articles = article_repo.list()
    num = 0
    Lu = 0
    for word in model.NewWord(username=user).word:
        Lu = WORD_DIFFICULTY_LEVEL[word] + Lu
        num += 1
    Lu = Lu / num
    if not is_no_article_matched(Lu, articles):
        raise NoArticleMatched(f"Unmatched article {user.username}")
    article_id=model.User(username=user).read_article(model.Article(article_id=Article_id))
    session.commit()
    return article_id
