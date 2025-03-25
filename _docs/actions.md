# How "RSS to LinkedIn" and "Auto Test (CI)" Work Together

The two workflows—**RSS to LinkedIn** and **Auto Test (CI)**—work in tandem to ensure that your app is continuously tested and deployed to LinkedIn, depending on the status of tests.

## **RSS to LinkedIn Workflow** Overview

This workflow is triggered either on a schedule (every hour) or manually (via a workflow dispatch). It performs several steps, but its key purpose is to run the app script and post to LinkedIn if everything is working properly.

### Key Steps in RSS to LinkedIn Workflow:
1. **Checkout Repository**: Retrieves the latest code from the repository.
2. **Setup Python**: Prepares the environment to run the app using Python 3.11.
3. **Install Dependencies**: Installs necessary dependencies using Pipenv.
4. **Check Test Status**: Before running the app, it checks whether tests have passed by inspecting the test status cache.
5. **Fail if Tests Failed**: If the tests failed in the last run (from the "Auto Test" workflow), it will stop this workflow from proceeding.
6. **Run Main App Script**: If the tests passed, it proceeds to run the main script that powers the application (which includes posting to LinkedIn).
7. **Save Blog Cache**: Saves any cache related to blog data for the next run.

## **Auto Test (CI) Workflow** Overview

The **Auto Test (CI)** workflow runs whenever changes are pushed to the `master` branch or triggered manually. This workflow's main role is to ensure that tests are executed before any deployment happens. If tests fail, it prevents the "RSS to LinkedIn" workflow from running.

### Key Steps in Auto Test Workflow:
1. **Checkout Repository**: Retrieves the latest code from the repository.
2. **Setup Python**: Prepares the environment to run Python 3.11.
3. **Install Dependencies**: Installs necessary dependencies with Pipenv.
4. **Run Tests**: Executes tests using `pytest`. If tests pass, the workflow will proceed; if not, it marks the test status as failed.
5. **Set Test Status**: The test status (pass or fail) is saved in a cache file that is later checked by the "RSS to LinkedIn" workflow to decide whether it should run.
6. **Save Test Status**: If the tests passed, the status is saved as "TRUE." If they failed, it's saved as "FALSE," which prevents the LinkedIn posting workflow from executing.

## How They Work Together

- **Test Flow**: The "Auto Test" workflow ensures that only passing tests trigger the **RSS to LinkedIn** workflow. If tests fail, the LinkedIn posting workflow is blocked.
  
- **Cache Mechanism**: Both workflows use a cache to store the status of the tests. The **RSS to LinkedIn** workflow checks this cache to decide whether to proceed with posting to LinkedIn.
  
- **Deployment to LinkedIn**: When tests pass, the "RSS to LinkedIn" workflow will trigger the main app script, which posts the content to LinkedIn. This ensures that only reliable, tested code is deployed.

## Conclusion

By linking these workflows, you ensure that only tested and stable code gets posted to LinkedIn, while any issues in testing prevent the social media posts from being published. This workflow guarantees that your app is continuously monitored and that content is only posted when it meets quality standards.
