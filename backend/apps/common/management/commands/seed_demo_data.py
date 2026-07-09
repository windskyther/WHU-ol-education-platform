"""Seed the database with official demo content (courses, posts, resources).

Usage:
    python manage.py seed_demo_data

Safe to re-run: it deletes and recreates only the content owned by the
official demo account (username="official_teacher"), so it never touches
real user data.
"""
import random
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.community.models import Post, Resource
from apps.courses.models import Chapter, Course
from apps.users.models import ensure_user_profile

User = get_user_model()

OFFICIAL_USERNAME = "official_teacher"
OFFICIAL_EMAIL = "official@whu-edu.demo"
OFFICIAL_PASSWORD = "OfficialDemo@2024"
OFFICIAL_DISPLAY_NAME = "WHU教研组"

COURSES = [
    {
        "title": "Python 编程入门",
        "description": "从零开始学习 Python 语法、数据类型与流程控制，适合零基础学员打好编程基础。",
        "category": "编程语言",
        "level": "beginner",
        "chapters": ["认识 Python 与开发环境", "变量与数据类型", "流程控制与循环", "函数与模块化编程"],
    },
    {
        "title": "数据结构与算法基础",
        "description": "系统讲解数组、链表、栈、队列、树与常见排序查找算法，配合代码实战巩固理解。",
        "category": "计算机基础",
        "level": "intermediate",
        "chapters": ["线性表：数组与链表", "栈与队列", "树与二叉树", "常见排序算法", "查找算法与复杂度分析"],
    },
    {
        "title": "Web 前端开发实战",
        "description": "掌握 HTML/CSS/JavaScript 核心知识，并学习 Vue 3 组件化开发，独立完成一个小型项目。",
        "category": "Web开发",
        "level": "intermediate",
        "chapters": ["HTML 与 CSS 基础", "JavaScript 核心语法", "Vue 3 组件化开发", "项目实战：待办事项应用"],
    },
    {
        "title": "机器学习入门",
        "description": "了解监督学习、无监督学习基本概念，动手实现线性回归与分类模型。",
        "category": "人工智能",
        "level": "advanced",
        "chapters": ["机器学习概述", "线性回归", "逻辑回归与分类", "模型评估与调优"],
    },
    {
        "title": "数据库原理与 MySQL 实践",
        "description": "讲解关系型数据库设计范式、SQL 查询优化，并结合 MySQL 完成真实场景练习。",
        "category": "数据库",
        "level": "beginner",
        "chapters": ["关系型数据库基础", "SQL 增删改查", "索引与查询优化", "事务与并发控制"],
    },
    {
        "title": "计算机网络基础",
        "description": "介绍 OSI/TCP-IP 分层模型、HTTP 协议与网络安全基础知识。",
        "category": "计算机基础",
        "level": "intermediate",
        "chapters": ["网络分层模型", "TCP/IP 协议详解", "HTTP 与 HTTPS", "常见网络安全问题"],
    },
    {
        "title": "算法竞赛入门指南",
        "description": "面向有一定编程基础的同学，讲解贪心、动态规划、图论等竞赛常用算法思路。",
        "category": "计算机基础",
        "level": "advanced",
        "chapters": ["贪心算法", "动态规划基础", "图论基础与最短路径", "经典例题解析"],
    },
]

POSTS = [
    ("experience", "我的 Python 自学之路", "从完全不懂编程到能独立写小项目，分享这半年的学习方法和踩过的坑，希望对大家有帮助。"),
    ("experience", "如何高效刷题巩固算法基础", "分享一套刷题节奏和复盘方法，重点在于举一反三而不是盲目刷题数量。"),
    ("qa", "Vue3 组件间通信有哪些方式？", "最近在做项目，父子组件、兄弟组件之间传值有点乱，求教有经验的同学指点一下常用方案。"),
    ("qa", "MySQL 索引失效的常见原因是什么？", "写了一条查询语句发现没有走索引，检查了字段类型和写法，还是没找到问题，求助。"),
    ("course_discussion", "《数据结构与算法基础》第三章笔记整理", "把树与二叉树这一章的重点内容整理了一下，欢迎大家补充和指正。"),
    ("course_discussion", "机器学习课程线性回归作业讨论", "关于作业里梯度下降的学习率设置，大家都是怎么调的？效果差异挺大的。"),
    ("chat", "暑假学习计划打卡帖", "开一个打卡帖，大家可以分享每天的学习进度，互相监督一下，一起坚持到暑假结束。"),
    ("chat", "有没有一起组队做课程项目的同学", "想找几个同学一起做前端实战项目，互相 review 代码，欢迎感兴趣的同学留言。"),
    ("experience", "网络协议章节的学习心得", "把 TCP 三次握手、四次挥手这块内容用图示的方式理解了一遍，思路清晰了很多，分享给大家。"),
    ("qa", "考试前如何复习效率更高？", "眼看要考试了，想请教一下大家是怎么安排复习时间和重点的。"),
    ("course_discussion", "Web 前端项目实战踩坑记录", "做待办事项应用的时候遇到了几个小问题，记录一下解决过程，供后面学习的同学参考。"),
    ("chat", "推荐几本编程入门书籍", "整理了几本自己看过觉得不错的入门书，涵盖 Python、算法和前端方向。"),
]

RESOURCES = [
    ("courseware", "Python 官方文档", "Python 语言权威参考手册，语法、标准库一应俱全。", "https://docs.python.org/zh-cn/3/"),
    ("courseware", "MDN Web Docs", "前端开发最权威的参考资料，涵盖 HTML/CSS/JavaScript 全部细节。", "https://developer.mozilla.org/zh-CN/"),
    ("tools", "VS Code 官网", "轻量强大的代码编辑器，支持丰富插件生态。", "https://code.visualstudio.com/"),
    ("tools", "Git 官方教程", "系统学习版本控制工具 Git 的免费官方教程。", "https://git-scm.com/book/zh/v2"),
    ("links", "LeetCode 算法练习", "海量算法题库，适合日常刷题巩固数据结构与算法。", "https://leetcode.cn/"),
    ("links", "菜鸟教程 - SQL 教程", "适合入门的 SQL 语法速查与练习网站。", "https://www.runoob.com/sql/sql-tutorial.html"),
    ("other", "机器学习课程课件合集", "本学期机器学习课程配套课件汇总打包，包含全部章节 PPT。", None),
    ("other", "数据结构与算法思维导图", "整理的数据结构与算法知识点思维导图，方便复习回顾。", None),
    ("courseware", "计算机网络分层模型图解", "OSI 与 TCP/IP 模型对比图解资料，配合课程讲义使用。", None),
    ("tools", "在线正则表达式测试工具", "快速验证正则表达式匹配效果的在线工具。", "https://regex101.com/"),
]


class Command(BaseCommand):
    help = "Seed official demo content (courses/chapters, forum posts, resource cards) for demos/acceptance."

    def handle(self, *args, **options):
        with transaction.atomic():
            teacher = self._ensure_official_teacher()
            self._reset_official_content(teacher)
            courses = self._seed_courses(teacher)
            posts = self._seed_posts(teacher)
            resources = self._seed_resources(teacher)

        self.stdout.write(self.style.SUCCESS(
            f"完成：官方账号 {OFFICIAL_USERNAME} / 密码 {OFFICIAL_PASSWORD}\n"
            f"课程 {len(courses)} 门，帖子 {len(posts)} 篇，资源 {len(resources)} 条。"
        ))

    def _ensure_official_teacher(self):
        user, created = User.objects.get_or_create(
            username=OFFICIAL_USERNAME,
            defaults={"email": OFFICIAL_EMAIL, "first_name": OFFICIAL_DISPLAY_NAME},
        )
        if created:
            user.set_password(OFFICIAL_PASSWORD)
            user.save()
        ensure_user_profile(user, role="teacher")
        return user

    def _reset_official_content(self, teacher):
        Course.objects.filter(teacher=teacher).delete()
        Post.objects.filter(author=teacher).delete()
        Resource.objects.filter(author=teacher).delete()

    def _seed_courses(self, teacher):
        created = []
        now = timezone.now()
        for item in COURSES:
            course = Course.objects.create(
                title=item["title"],
                description=item["description"],
                category=item["category"],
                level=item["level"],
                teacher=teacher,
                is_published=True,
                published_at=now,
            )
            for order, chapter_title in enumerate(item["chapters"], start=1):
                Chapter.objects.create(
                    course=course,
                    title=chapter_title,
                    description="",
                    order=order,
                )
            created.append(course)
        return created

    def _seed_posts(self, teacher):
        created = []
        for category, title, content in POSTS:
            post = Post.objects.create(
                author=teacher,
                title=title,
                content=content,
                category=category,
                likes_count=random.randint(3, 40),
                favorites_count=random.randint(1, 15),
                comments_count=random.randint(0, 10),
            )
            created.append(post)
        return created

    def _seed_resources(self, teacher):
        created = []
        for category, title, description, url in RESOURCES:
            resource = Resource(
                author=teacher,
                title=title,
                description=description,
                category=category,
                url=url or "",
                likes_count=random.randint(2, 30),
                favorites_count=random.randint(1, 12),
                comments_count=random.randint(0, 8),
            )
            if not url:
                filename = f"{title}.txt"
                content = f"{title}\n\n{description}\n\n(由官方演示数据自动生成的占位资料文件)"
                resource.original_name = filename
                resource.content_type = "text/plain"
                resource.file.save(filename, ContentFile(content.encode("utf-8")), save=False)
                resource.size = len(content.encode("utf-8"))
            resource.save()
            created.append(resource)
        return created
