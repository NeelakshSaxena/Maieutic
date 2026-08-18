# MentorAI — Knowledge Graph

## 1. Purpose

Represent relationships between concepts.

## 2. Node Types

- Concept
- Skill
- Subject
- Problem
- Project
- Misconception
- Resource

## 3. Relationship Types

PREREQUISITE_OF

RELATED_TO

PART_OF

USED_IN

CONFUSED_WITH

REINFORCES

REQUIRES

## 4. Example

Arrays
    |
    +--> Sorting
    |
    +--> Binary Search
            |
            +--> Lower Bound
            |
            +--> Upper Bound

Binary Search
    |
    +--> Divide and Conquer

## 5. Mastery Propagation

If a student repeatedly demonstrates mastery of a concept, dependent concepts may receive prerequisite confidence.

However, mastery must not be automatically transferred without evidence.

## 6. Graph Storage

MVP:

PostgreSQL relational representation.

Qdrant:

Semantic retrieval.

Future:

Dedicated graph database if graph scale requires it.

## 7. Concept Identity

Every concept must have a stable canonical ID.

Example:

cs.algorithms.search.binary_search

This prevents duplicate concepts such as:

"Binary Search"

"binary search"

"Binary Searching"