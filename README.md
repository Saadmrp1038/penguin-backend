# PenguinLLM Backend

## Overview

The PenguinLLM backend powers a knowledge base platform with both admin and client-facing features. Admins can submit questions, answers, and website links, which are automatically scraped and parsed into the knowledge base. The client side allows users to interact with a chatbot that provides answers using the knowledge base. If a user finds an answer unsatisfactory, they can report it, prompting admins to update the knowledge base.

To enrich the knowledge base, the system scrapes all pages of submitted websites, as well as the knowledge base is pre-populated with data from platforms like Fiverr and Upwork, to gather comprehensive data.

## Features

- **Admin Panel**:
  - Admins can submit and manage questions, answers, and website links.
  - Automatically scrapes entire websites submitted by admins and adds relevant content to the knowledge base.

- **Client Chat Interface**:
  - Users interact with a chatbot that pulls answers from the knowledge base.
  - Users can report issues with chatbot responses, flagging them for admin review and updates.

- **Automated Scraping**:
  - The Scrapy-based scraper extracts data from all pages of submitted websites.
  - Large-scale scraping of platforms like Fiverr and Upwork has been used to pre-populate the knowledge base with hundreds of articles.

## Tech Stack

### Backend
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/): High-performance web framework for building APIs with Python.
- **Database**: [PostgreSQL](https://www.postgresql.org/): Storing the knowledge base data and reports.
- **ORM**: [SQLAlchemy](https://www.sqlalchemy.org/): Used for managing database interactions.
- **Web Scraping**: [Scrapy](https://scrapy.org/): Used to scrape data from all pages of submitted websites and large platforms.

### Deployment
- **Automation**: GitHub Actions is used for Continuous Deployment. Pushing code to the GitHub repository triggers an automated deployment to a DigitalOcean droplet.
- **Server**: The application is served on a DigitalOcean droplet using [Nginx](https://www.nginx.com/) for reverse proxy and load balancing.

## API Documentation

The PenguinLLM backend provides a comprehensive and interactive API documentation built with FastAPI’s Swagger UI. You can explore all the available endpoints and their usage in detail.

- **Live API Documentation**: [https://penguapi.priyolab.net/docs](https://penguapi.priyolab.net/docs)

## Installation and Setup

### Prerequisites
- **Python 3.9+**: Ensure you have Python installed.
- **PostgreSQL**: Set up a PostgreSQL database for the knowledge base.
- **GitHub Actions**: Ensure proper setup for CI/CD with GitHub Actions.
- **Nginx**: Configure Nginx on the DigitalOcean droplet for serving the app.

### Deployment

The deployment process is automated using GitHub Actions. Pushing to the main branch triggers a workflow that builds and deploys the backend to a DigitalOcean droplet.

To configure the workflow:
1. Update the `.github/workflows/deploy.yml` file with your deployment details.
2. Push changes to the repository, and the workflow will handle the rest, deploying the changes to your droplet.
