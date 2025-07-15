---
layout: default
title: Fact-Checked News
---

# Fact-Checked News

Welcome to our fact-checked news aggregator! This site contains verified factual claims extracted from news articles and fact-checked against reliable sources.

## Recent Fact Checks

{% for post in site.posts %}
### [{{ post.title }}]({{ post.url }})
**Verified:** {{ post.verified | capitalize }}  
**Source:** {% if post.source %}{{ post.source }}{% else %}No source available{% endif %}

{{ post.excerpt }}

---
{% endfor %} 