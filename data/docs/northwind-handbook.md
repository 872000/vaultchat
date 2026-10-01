# Northwind Labs — Project Handbook

Northwind Labs builds data tooling for small retailers. This handbook covers how the engineering team works.

## Mission

We help independent retailers understand their sales data without hiring a data team. Our flagship product, ShelfSight, ingests point-of-sale exports and produces weekly restock recommendations.

## Tech Stack

The backend is Java with Spring Boot and PostgreSQL. The frontend is React with TypeScript. Infrastructure runs on AWS: ECS for services, RDS for the database, and S3 for file storage. CI/CD is handled by GitHub Actions, and every pull request must pass the full test suite before merging.

## Team Rituals

Standup is at 9:30 AM Eastern, Monday through Friday, and lasts no more than fifteen minutes. Sprint planning happens every other Monday. Code reviews should be completed within one business day; the author is responsible for pinging reviewers if a review stalls.

## Definition of Done

A task is done when the code is merged to main, tests cover the new behavior, documentation is updated, and the change is deployed to staging. Anything short of that is not done.

## On-call

On-call rotates weekly. The primary responder acknowledges alerts within fifteen minutes during business hours. Every incident gets a blameless postmortem within two business days, and action items are tracked as regular sprint tasks.

## Hiring Bar

We hire for slope over y-intercept: curiosity, communication, and the ability to learn matter more than years of experience. Every candidate completes a take-home exercise reviewed blind, followed by a pair-programming session.
