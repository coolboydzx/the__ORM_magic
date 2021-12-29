# ORM
# **标题**

项目名称：Lab 3 : The ORM Magic and The Service Layer

团队小组成员：董泽翔、段佐翼、徐毅、周宇峰、张祯辰

日期：2021/12/25

# **摘要**

为了实现理解依赖倒置、实现一个服务层，供用户阅读文章与实践测试驱动开发（TDD）。本文在ORM 导入了域模型，我们使用 SQLAlchemy 的抽象来定义数据库表和列。调用，我们将能够轻松地将域模型实例从数据库加载和保存到数据库。因为ORM 取决于模型，所以实现了依赖关系的反转。

# **介绍**

在本文章中，介绍了如何通过遵循依赖项反转的原则来保持域模型的纯净--让基础结构依赖于域模型，而不是域模型依赖于基础结构。此外，还有在服务中实现服务层。py代表EnglishPal，它提供一个称为read的核心服务。该服务将为用户选择合适的文章阅读。函数read接受以下四个参数作为输入，如果已成功为用户分配了要读取的项目，则返回项目ID材料和方法。

> 操作系统：Windows10旗舰版
>
> 硬件配置：内存：金士顿16G DDR4 3200
>
> Cpu：Intel CORE i7
>
> 硬盘：SSD 512g
>
> 开发平台： PyCharm
>
> 开发语言： Python
>
> 方法：使用SQLAlchemy的ORM（对象关系映射器）将类映射到数据库表；测试驱动开发（TDD）。

# **结果**

项目地址：

**修改后的orm.py:**

```python
from sqlalchemy import Table, MetaData, Column, Integer, String, Date, ForeignKey, create_engine
from sqlalchemy.orm import mapper, relationship

import model

metadata = MetaData()

articles = Table(
    'articles',
    metadata,
    Column('article_id', Integer, primary_key=True, autoincrement=True),
    Column('text', String(10000)),
    Column('source', String(100)),
    Column('date', String(10)),
    Column('level', Integer, nullable=False),
    Column('question', String(1000)),
    )


users = Table(
    'users',
    metadata,
    Column('username', String(100), primary_key=True),
    Column('password', String(64)),
    Column('start_date', String(10), nullable=False),
    Column('expiry_date', String(10), nullable=False),
    )

newwords = Table(
    'newwords',
    metadata,
    Column('word_id', Integer, primary_key=True, autoincrement=True),
    Column('username', String(100), ForeignKey('users.username')),
    Column('word', String(20)),
    Column('date', String(10)),
    )

readings = Table(
    'readings',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('username', String(100), ForeignKey('users.username')),
    Column('article_id', Integer, ForeignKey('articles.article_id')),
    )


def start_mappers():
    # articles_mapper = mapper(model.Article,articles)
    # users_mapper = mapper(model.User, users)
    # metadata.create_all(create_engine('sqlite:///EnglishPalDatabase.db'))
    articles_mapper=mapper(model.Article, articles)
    mapper(model.NewWord, newwords)
    mapper(model.User, users,
           properties={
               "_read": relationship(
                   articles_mapper,secondary=readings,collection_class=[]
               )
           }
)
	mapper(model.Reading, readings)

```

修改后的services.py：

```python
WORD_DIFFICULTY_LEVEL = {'starbucks': 5, 'luckin': 4, 'secondcup': 4, 'costa': 3, 'timhortons': 3, 'frappuccino': 6}
import model


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
    global article_id
    min = 0
    article_id = 0
    for La in articles:
        if (La.level >= Lu):
            if (min == 0):
                min = La.level
                article_id = La.article_id
            else:
                if (min > La.level):
                    min = La.level
                    article_id = La.article_id
    if min == 0:
        return False
    else:
        return True


def read(user, user_repo, article_repo, session):
    users = user_repo.list()
    if not is_unknown_user(user.username, users):
        raise UnknownUser(f"Unknown user {user.username}")
    if not is_unknown_password(user.password, users):
        raise UnknownUser(f"Unknown password {user.password}")
    articles = article_repo.list()
    num = 0
    Lu = 0
    words = session.execute(
        'SELECT word FROM newwords WHERE username=:username',
        dict(username=user.username),
    )
    # words = model.NewWord(username=user.username)
    # wordss = dict(words)
    for word in words:
        Lu = WORD_DIFFICULTY_LEVEL[word[0]] + Lu
        num += 1
    if num == 0:
        raise NoArticleMatched(f"Unmatched article {user.username}")
    # 由于数据库中都不大于三，所以直接除以num
    Lu = round(Lu / num) + 1
    if not is_no_article_matched(Lu, articles):
        raise NoArticleMatched(f"Unmatched article {user.username}")
    session.add(model.Reading(user.username, article_id))

    session.commit()
    return article_id

```

# **讨论**

修改工作的原因如下：

在orm.py中添加start_mappers函数。

在ORM 导入了域模型，我们使用 SQLAlchemy 的抽象来定义数据库表和列。当我们调用该函数时，SQLAlchemy 就会将我们的域模型类绑定到我们定义的各种表中。start_mappers函数是一个映射，关联了域模型和关系数据库，这就导致一旦我们调用 ，我们将能够轻松地将域模型实例从数据库加载和保存到数据库。因为ORM 取决于模型，所以实现了依赖关系的反转。

 在service.py中添加 is_unknown_user、is_unknown_password、is_no_article_matched、read函数。接下里分别分析每个函数的作用：

- is_unknown_user：判断用户名
- is_unknown_password：判断密码
- is_no_article_matched：文章库中没有文章或文章库中没有文章的难度与用户的词汇量相匹配
- Read：这个函数的功能是为用户选择一个合适的文章来阅读。函数read的输入有四个参数user、user repo、article repo
- session，如果用户被成功分配到一篇文章，则返回一个文章ID。
- user：一个用户对象。在model.py中定义了User这个类。User有一个重要的方法叫做read article。
- user repo：一个 UserRepository 对象。类 UserRepository 在 repository.py 中定义。
- article repo: 一个ArticleRepository对象。ArticleRepository类定义在repository.py中。
- session：一个SQLAlchemy会话对象。

如果用户没有正确的用户名或密码，函数 read会引发一个 UnknownUser 异常，或者如果文章库中没有文章，会引发一个 NoArticleMatched 异常。

如果文章库（即文章库）中没有文章的难度与用户的词汇量相匹配，则引发NoArticleMatched异常。我们说一篇文章的难度等级La与用户的词汇等级Lu相匹配，如果La>Lu。如果有多篇文章满足La > Lu，那么选择La最小的一篇。

关于函数是否在服务中读取、py是否遵循单一责任原则（SRP）原则。原因如下：

遵循单一责任原则，简单来说就是一个对象或者方法，只做一件事。

那首先分析services.py中每一个对象和方法的功能：

- UnknownUser：定义了用户名判断的类

- NoArticleMatched：定义了文章匹配的类

- is_unknown_user：判断用户名

- is_unknown_password：判断密码

- is_no_article_matched：文章库中没有文章或文章库中没有文章的难度与用户的词汇量相匹配

- Read：为用户选择一个合适的文章来阅读。

可见，上述任何一个模块都有清晰的边界，都只对某一类行为者负责。所以遵循单一责任原则。

# **引用**

[1]Martin Fowler.Patterns of Enterprise Application Architecture 1st Edition[M].Addison-Wesley Professional; 1st edition (November 5, 2002)：33-53

[2]Eric Evans.Domain-Driven Design: Tackling Complexity in the Heart of Software 1st Edition[M].Addison-Wesley Professional; 1st edition (August 20, 2003):102-108
