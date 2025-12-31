# LLM as Judge - User Stories

User stories for the LLM as Judge feature in Eval Forge, written in Gherkin format.

---

## Feature: LLM as Judge Configuration

```gherkin
Feature: LLM as Judge Configuration
  As an Eval Forge user
  I want to enable LLM as Judge for my evaluations
  So that I can get multi-dimensional quality assessments of model responses

  Background:
    Given I am logged into Eval Forge
    And I have at least one model configured as a target
    And I have at least one model configured as a judge

  Scenario: Enable LLM as Judge when creating an evaluation
    Given I am on the Evaluations page
    When I click to create a new evaluation
    And I provide a valid evaluation name
    And I select a target model from the dropdown
    And I upload a valid dataset
    And I toggle "Enable LLM as Judge" to ON
    Then I should see the judge configuration options appear
    And I should see a "Judge Model" dropdown
    And I should see a "Custom Prompt Template" textarea

  Scenario: Select a judge model for evaluation
    Given I am creating a new evaluation
    And I have enabled "LLM as Judge"
    When I click on the "Judge Model" dropdown
    Then I should see a list of all configured models
    When I select a model as the judge
    Then the selected model should be displayed in the dropdown

  Scenario: Create evaluation with LLM as Judge disabled
    Given I am on the Evaluations page
    When I create a new evaluation without enabling LLM as Judge
    Then the evaluation should be created successfully
    And the evaluation should use traditional metrics only
    And no judge scores should be calculated during run

  Scenario: View default judge prompt template
    Given I am creating a new evaluation with LLM as Judge enabled
    When I view the "Custom Prompt Template" textarea
    Then I should see the default judge prompt template pre-populated
    And the template should include placeholders for question, expected answer, and model response
```

---

## Feature: Custom Judge Prompt Template

```gherkin
Feature: Custom Judge Prompt Template
  As an Eval Forge user
  I want to customize the judge evaluation prompt
  So that I can tailor the evaluation criteria to my specific use case

  Background:
    Given I am logged into Eval Forge
    And I am creating a new evaluation with LLM as Judge enabled

  Scenario: Use default judge prompt template
    Given the "Custom Prompt Template" textarea shows the default template
    When I create the evaluation without modifying the template
    Then the evaluation should use the default judge prompt
    And the judge should evaluate on Accuracy, Relevance, Clarity, and Completeness

  Scenario: Customize judge prompt template
    Given I want to add custom evaluation criteria
    When I modify the "Custom Prompt Template" textarea
    And I add a new evaluation dimension "Conciseness"
    And I save the evaluation
    Then the custom prompt template should be stored with the evaluation

  Scenario: Reset custom prompt to default
    Given I have modified the custom prompt template
    When I click a "Reset to Default" button
    Then the prompt template should revert to the default template
    And my custom changes should be discarded
```

---

## Feature: Running Evaluation with LLM Judge

```gherkin
Feature: Running Evaluation with LLM Judge
  As an Eval Forge user
  I want to run evaluations that use LLM as Judge
  So that each response is evaluated by a stronger model for quality

  Background:
    Given I am logged into Eval Forge
    And I have created an evaluation with LLM as Judge enabled
    And the target model is accessible
    And the judge model is accessible

  Scenario: Run evaluation with LLM judge enabled
    Given I am on the Evaluations page
    When I click "Run" on an evaluation with LLM as Judge enabled
    Then the evaluation should start processing
    And for each question in the dataset:
      | Step                              |
      | Target model generates a response |
      | Judge model evaluates the response|
      | Scores and reasoning are stored   |
    And the evaluation should complete with judge scores

  Scenario: Judge scores individual responses on multiple dimensions
    Given an evaluation is running with LLM as Judge
    When the judge model evaluates a response
    Then the judge should provide scores for:
      | Dimension    | Scale |
      | Accuracy     | 1-5   |
      | Relevance    | 1-5   |
      | Clarity      | 1-5   |
      | Completeness | 1-5   |
      | Overall      | 1-5   |
    And the judge should provide reasoning for the scores

  Scenario: Calculate aggregate judge scores
    Given an evaluation with LLM as Judge has completed
    When all questions have been evaluated
    Then the system should calculate aggregate scores:
      | Metric                 |
      | Average Judge Accuracy |
      | Average Judge Relevance|
      | Average Judge Clarity  |
      | Average Judge Completeness|
      | Average Judge Overall  |
    And store these on the evaluation record

  Scenario: Handle judge model failure gracefully
    Given an evaluation is running with LLM as Judge
    When the judge model fails to respond for a question
    Then the result should be saved with null judge scores
    And an error message should be logged
    And the evaluation should continue with the next question
    And the user should be notified of partial judge results
```

---

## Feature: Viewing Judge Evaluation Results

```gherkin
Feature: Viewing Judge Evaluation Results
  As an Eval Forge user
  I want to view the LLM judge scores and reasoning
  So that I can understand the quality of my model's responses in detail

  Background:
    Given I am logged into Eval Forge
    And I have completed an evaluation with LLM as Judge enabled
    And the results contain judge scores

  Scenario: View aggregate judge scores in results summary
    Given I am on the Results page
    When I view an evaluation that used LLM as Judge
    Then I should see a "Judge Scores Summary" section
    And I should see visual indicators (bars/gauges) for:
      | Score               | Display            |
      | Avg Judge Accuracy  | Score bar 1-5      |
      | Avg Judge Relevance | Score bar 1-5      |
      | Avg Judge Clarity   | Score bar 1-5      |
      | Avg Judge Completeness | Score bar 1-5   |
      | Avg Judge Overall   | Highlighted score  |

  Scenario: View individual question judge scores
    Given I am viewing the detailed results of an evaluation
    When I expand a single question result
    Then I should see the model's response
    And I should see the judge scores for that question
    And I should see the judge's reasoning in an expandable panel

  Scenario: View judge reasoning for a question
    Given I am viewing a question result with judge scores
    When I click to expand the judge reasoning
    Then I should see the judge's explanation
    And the reasoning should explain why each dimension received its score

  Scenario: Filter results by judge score
    Given I am viewing the Results page
    When I select a filter option "Show Low Judge Scores"
    Then I should only see results where any judge score is below a threshold
    And I can identify which questions need improvement

  Scenario: Compare traditional metrics with judge scores
    Given I am viewing an evaluation result
    When I look at the results
    Then I should see traditional metrics (if calculated)
    And I should see judge scores side by side
    So I can compare automated metrics with LLM judgment
```

---

## Feature: Results Without LLM Judge

```gherkin
Feature: Results Without LLM Judge
  As an Eval Forge user
  I want evaluations without LLM as Judge to work as before
  So that the feature is backwards compatible

  Background:
    Given I am logged into Eval Forge

  Scenario: View results for evaluation without LLM judge
    Given I have completed an evaluation without LLM as Judge
    When I view the results on the Results page
    Then I should see traditional evaluation metrics
    And I should NOT see any judge score sections
    And the results display should look the same as before the feature

  Scenario: Historical evaluations display correctly
    Given I have evaluations from before the LLM as Judge feature
    When I view those historical results
    Then the results should display correctly
    And no judge-related fields should appear
    And no errors should occur
```

---

## Feature: Model Selection for Judge Role

```gherkin
Feature: Model Selection for Judge Role
  As an Eval Forge user
  I want to select any configured model as a judge
  So that I can use different models for evaluation purposes

  Background:
    Given I am logged into Eval Forge
    And I have multiple models configured:
      | Name          | Endpoint                  | Model       |
      | Llama Target  | http://localhost:11434    | llama3.2    |
      | Llama Judge   | http://localhost:11434    | llama3.2    |
      | GPT-4 Judge   | https://api.openai.com    | gpt-4       |

  Scenario: Use same model as target and judge
    Given I am creating an evaluation
    When I select "Llama Target" as the target model
    And I enable LLM as Judge
    And I select "Llama Target" as the judge model
    Then the evaluation should be created successfully
    And the same model will generate and judge responses

  Scenario: Use different model as judge
    Given I am creating an evaluation
    When I select "Llama Target" as the target model
    And I enable LLM as Judge
    And I select "GPT-4 Judge" as the judge model
    Then the evaluation should be created successfully
    And a stronger model will judge the target's responses

  Scenario: Judge model connectivity check
    Given I am creating an evaluation with LLM as Judge
    When I select a judge model
    And the judge model endpoint is not reachable
    Then I should receive a warning about judge model connectivity
    But I should still be able to create the evaluation
```

---

## Feature: API Support for LLM Judge

```gherkin
Feature: API Support for LLM Judge
  As a developer using the Eval Forge API
  I want to access LLM judge functionality programmatically
  So that I can integrate it into my automation workflows

  Scenario: Create evaluation with judge via API
    Given I have a valid API session
    When I POST to /api/evaluations with:
      | Field                 | Value           |
      | name                  | API Judge Test  |
      | model_id              | 1               |
      | use_llm_judge         | true            |
      | judge_model_id        | 2               |
      | judge_prompt_template | null (default)  |
    Then the response status should be 201
    And the evaluation should be created with judge configuration

  Scenario: Get default judge prompt template via API
    Given I have a valid API session
    When I GET /api/judge-prompts/default
    Then the response status should be 200
    And the response should contain the default prompt template
    And the template should include scoring instructions

  Scenario: Retrieve evaluation results with judge scores via API
    Given I have completed an evaluation with LLM as Judge
    When I GET /api/evaluations/{id}/results
    Then the response should include for each result:
      | Field                  |
      | judge_accuracy_score   |
      | judge_relevance_score  |
      | judge_clarity_score    |
      | judge_completeness_score|
      | judge_overall_score    |
      | judge_reasoning        |
    And the evaluation should include aggregate scores
```

---

## Feature: Database Migration for Judge Fields

```gherkin
Feature: Database Migration for Judge Fields
  As a system administrator
  I want to migrate the database to support LLM judge fields
  So that the new feature works with existing installations

  Scenario: Run migration on existing database
    Given I have an existing Eval Forge database
    And the database does not have judge-related columns
    When I run the judge fields migration script
    Then the evaluations table should have new columns:
      | Column                | Type    |
      | judge_model_id        | INTEGER |
      | use_llm_judge         | BOOLEAN |
      | judge_prompt_template | TEXT    |
      | avg_judge_accuracy    | FLOAT   |
      | avg_judge_relevance   | FLOAT   |
      | avg_judge_clarity     | FLOAT   |
      | avg_judge_completeness| FLOAT   |
      | avg_judge_overall     | FLOAT   |
    And the results table should have new columns:
      | Column                   | Type  |
      | judge_accuracy_score     | FLOAT |
      | judge_relevance_score    | FLOAT |
      | judge_clarity_score      | FLOAT |
      | judge_completeness_score | FLOAT |
      | judge_overall_score      | FLOAT |
      | judge_reasoning          | TEXT  |
      | judge_raw_response       | TEXT  |

  Scenario: Migration preserves existing data
    Given I have an existing database with evaluations and results
    When I run the judge fields migration script
    Then all existing evaluations should be preserved
    And all existing results should be preserved
    And new judge columns should have NULL values for existing records
```
