# Interview Prep Notes

## Behavioral Questions

Use the STAR method: Situation, Task, Action, Result. Keep each story under two minutes. Prepare stories for conflict resolution, a missed deadline, a technical disagreement, mentoring someone, and a project you are proud of. Quantify results whenever possible: numbers make stories memorable.

## Data Structures

Know the trade-offs cold. Arrays give O(1) random access but O(n) insertion in the middle. Hash maps give average O(1) lookup, insert, and delete. Heaps give O(log n) push and pop and O(1) peek, which makes them ideal for top-k problems. Practice implementing a hash map from scratch at least once.

## Algorithms

Binary search runs in O(log n) on sorted data and is easy to get wrong on boundaries, so practice the edge cases. Breadth-first search is the right tool for shortest paths in unweighted graphs. Know quicksort and mergesort: quicksort is fast in practice with O(n log n) average time, while mergesort guarantees O(n log n) at the cost of O(n) extra space.

## System Design

Start by clarifying requirements and estimating scale. A typical answer covers the API, the data model, and the key components: load balancer, application servers, cache, database, and message queue. Mention trade-offs explicitly: consistency versus availability, SQL versus NoSQL, synchronous versus asynchronous processing. Always discuss bottlenecks and how you would monitor them.

## The Night Before

Sleep matters more than cramming. Lay out your setup, test your microphone and camera, and review your STAR stories once. Arrive ten minutes early with water nearby and a notebook ready.
