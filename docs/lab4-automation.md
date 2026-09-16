---
layout: default
title: Lab 4 - Workflow Automation
nav_order: 6
---

# ⚡ Lab 4: Automating AI Usage Monitoring

**Duration:** ~30 minutes

In this lab, you will create a Dynatrace Workflow that analyses token usage for your AI service and sends a notification when usage exceeds a defined threshold.

This turns the DQL analysis created in Lab 2 into a repeatable automated process.

---

## 🎯 Learning Objectives

By the end of this lab, you will be able to:

- Create and run a Dynatrace Workflow
- Execute a DQL query from a workflow
- Enrich token data with model pricing from a Grail lookup table
- Add a condition based on token usage
- Include query results in a notification
- Test and review a workflow execution

---

<div class="why-dynatrace" markdown="1">

## 🏆 From Analysis to Automation

In Lab 2, you manually queried token usage and estimated model cost.

A workflow allows the same analysis to run automatically.

| Manual analysis | Automated workflow |
|---|---|
| Open a Notebook | Run on a schedule |
| Execute DQL manually | Execute DQL automatically |
| Review the result | Evaluate a condition |
| Decide whether action is needed | Run a notification task |
| Repeat the process later | Reuse the same workflow |

The workflow does not automatically determine whether token usage is good or bad. You define the query, threshold, and resulting action.

</div>

---

## Step 1: Prepare the Workshop Data

Before creating the workflow, make sure your service has recent trace data.

### 1.1 Generate additional traffic

Open the AI Chat interface and send several messages with **Use Knowledge Base (RAG)** enabled.

Example questions:

```text
What is Dynatrace?
```

```text
How does OpenTelemetry work with Dynatrace?
```

```text
Explain how Grail supports observability analysis.
```

Each RAG request generates two LLM calls, giving the workflow enough token data to analyse.

### 1.2 Verify the pricing lookup table

Open a Dynatrace Notebook and run:

```dql
load "/lookups/ai/bedrock/model-costs"
```

The result should include pricing records for:

- `workshop-chat`
- `us.amazon.nova-micro-v1:0`

The lookup fields should be:

- `model`
- `input_cost_per_million_usd`
- `output_cost_per_million_usd`

Do not continue if the lookup table cannot be loaded.

---

## Step 2: Create the Workflow

### 2.1 Open Workflows

1. Open **Workflows** in Dynatrace.
2. Select **+ Workflow**.
3. Create a new workflow.
4. Name it:

```text
AI Usage Monitor - {YOUR_ATTENDEE_ID}
```

### 2.2 Select a trigger

Select a **Time interval trigger**.

For the workshop, configure it to run every:

```text
15 minutes
```

You will also run the workflow manually, so you do not need to wait for the scheduled execution.

> 💡 In a real environment, the schedule should reflect the required monitoring frequency and the expected volume of telemetry.

---

## Step 3: Add the Token-Usage Query

### 3.1 Add a DQL task

1. Add a new task after the trigger.
2. Select **Execute DQL query**.
3. Name the task:

```text
get_token_usage
```

4. Configure the query timeframe to include the traffic generated during the workshop.
5. Paste the following DQL:

```dql
// Calculate token usage and estimated cost for this attendee
fetch spans
| filter service.name == "ai-chat-service-{YOUR_ATTENDEE_ID}"
| filter isNotNull(gen_ai.usage.input_tokens)
| summarize
    total_input_tokens = sum(gen_ai.usage.input_tokens),
    total_output_tokens = sum(gen_ai.usage.output_tokens),
    avg_input_tokens = avg(gen_ai.usage.input_tokens),
    avg_output_tokens = avg(gen_ai.usage.output_tokens),
    request_count = count(),
    by: {gen_ai.response.model}
| fieldsAdd total_tokens =
    total_input_tokens + total_output_tokens
| lookup [load "/lookups/ai/bedrock/model-costs"],
    sourceField:gen_ai.response.model,
    lookupField:model,
    prefix:"pricing."
| filter isNotNull(pricing.model)
| fieldsAdd estimated_cost_usd =
    (
        total_input_tokens * pricing.input_cost_per_million_usd
        + total_output_tokens * pricing.output_cost_per_million_usd
    ) / 1000000.0
| fields
    gen_ai.response.model,
    request_count,
    total_input_tokens,
    total_output_tokens,
    total_tokens,
    avg_input_tokens,
    avg_output_tokens,
    estimated_cost_usd
| sort total_tokens desc
```

### 3.2 Test the task

Use the task's test or run option.

The result should contain at least one record with:

- The recorded model
- Request count
- Input tokens
- Output tokens
- Total tokens
- Estimated cost

The estimated cost will be very small. This is expected because Amazon Nova Micro is inexpensive and the workshop generates limited traffic.

### 3.3 Understand the result

The workflow query:

1. Retrieves spans for your attendee-specific service
2. Keeps spans that contain input-token usage
3. Aggregates token consumption by model
4. Loads the Bedrock pricing lookup
5. Matches the recorded model with its pricing
6. Calculates the estimated model cost

The query supports both model identifiers stored in the lookup table.

---

## Step 4: Add a Usage Condition

### 4.1 Add a condition

Add a **Condition** task after `get_token_usage`.

Configure the condition to continue only when the first result contains more than 1,000 total tokens:

{% raw %}

```text
{{ result("get_token_usage").records[0].total_tokens > 1000 }}
```

{% endraw %}

> 💡 The threshold is deliberately low so that the condition can be tested during the workshop. It is not a recommended production threshold.

### 4.2 Connect the tasks

The workflow should now follow this structure:

```text
Time interval trigger
  └── get_token_usage
      └── Condition: total_tokens > 1000
```

The notification task created in the next step should run only when the condition evaluates to `true`.

### 4.3 Handle an empty result

If the DQL task returns no records, the condition cannot access `records[0]`.

Before running the workflow, confirm that:

- The application generated recent traffic
- The service name contains the correct attendee ID
- The query timeframe includes that traffic
- The pricing lookup contains the model value recorded in the spans

---

## Step 5: Add a Notification

The available notification actions depend on the connections configured in the workshop environment.

Use an **Email**, **Microsoft Teams**, or **Slack** action provided by the instructor.

If no notification connection is available, you can still complete the workflow by reviewing the DQL and condition task results in the execution log.

### 5.1 Add the notification task

Add the selected notification action after the condition.

Name the task:

```text
send_usage_alert
```

### 5.2 Configure the message

Use the following content:

{% raw %}

```text
AI usage notification

Service: ai-chat-service-{YOUR_ATTENDEE_ID}
Model: {{ result("get_token_usage").records[0]["gen_ai.response.model"] }}

Token usage:
- Requests: {{ result("get_token_usage").records[0].request_count }}
- Input tokens: {{ result("get_token_usage").records[0].total_input_tokens }}
- Output tokens: {{ result("get_token_usage").records[0].total_output_tokens }}
- Total tokens: {{ result("get_token_usage").records[0].total_tokens }}

Estimated model cost:
${{ result("get_token_usage").records[0].estimated_cost_usd }}

This notification was generated by the Dynatrace AI observability workshop.
```

{% endraw %}

> The exact expression editor and field-access syntax can vary by workflow action. Use the expression suggestions displayed by the workflow editor to select values from `get_token_usage`.

### 5.3 Add a subject if required

For an email action, use:

```text
AI usage notification - {YOUR_ATTENDEE_ID}
```

For Microsoft Teams or Slack, use the same text as the message title if the action supports one.

---

## Step 6: Save and Test the Workflow

### 6.1 Review the workflow

Your completed workflow should look like:

```text
Time interval trigger
  └── Execute DQL: get_token_usage
      └── Condition: total_tokens > 1000
          └── Notification: send_usage_alert
```

### 6.2 Save the workflow

Select **Save draft** or the equivalent save option shown in the Workflows app.

### 6.3 Run the workflow manually

Select **Run**.

A manual execution allows you to test the tasks without waiting for the scheduled trigger.

### 6.4 Review the execution

Open the workflow execution and inspect each task.

Confirm that:

1. `get_token_usage` completed successfully
2. The DQL task returned at least one record
3. The condition evaluated to `true` or `false`
4. The notification ran only when the condition was `true`
5. The execution completed without an unhandled error

### 6.5 Test the false path

Temporarily increase the condition to a value larger than your recorded token usage:

{% raw %}

```text
{{ result("get_token_usage").records[0].total_tokens > 1000000 }}
```

{% endraw %}

Run the workflow again.

The condition should evaluate to `false`, and the notification task should not run.

Restore the workshop threshold afterwards:

{% raw %}

```text
{{ result("get_token_usage").records[0].total_tokens > 1000 }}
```

{% endraw %}

This confirms that the workflow does not send a notification on every execution.

---

## Step 7: Extend the Workflow with a Usage Summary

If time permits, add a second DQL task that identifies the operations consuming the most tokens.

### 7.1 Add the query

Create another **Execute DQL query** task named:

```text
get_usage_by_operation
```

Use:

```dql
// Token usage by operation
fetch spans
| filter service.name == "ai-chat-service-{YOUR_ATTENDEE_ID}"
| filter isNotNull(gen_ai.usage.input_tokens)
| summarize
    total_input_tokens = sum(gen_ai.usage.input_tokens),
    total_output_tokens = sum(gen_ai.usage.output_tokens),
    avg_input_tokens = avg(gen_ai.usage.input_tokens),
    avg_output_tokens = avg(gen_ai.usage.output_tokens),
    maximum_input_tokens = max(gen_ai.usage.input_tokens),
    request_count = count(),
    by: {span.name, gen_ai.response.model}
| fieldsAdd total_tokens =
    total_input_tokens + total_output_tokens
| sort total_tokens desc
| limit 10
```

### 7.2 Review the result

Use the result to identify:

- Which LLM operation consumed the most tokens
- Whether input tokens or output tokens dominate
- Whether one operation has an unusually high average
- Whether a small number of requests generated most of the usage

Do not add token totals from parent workflow spans and child LLM spans unless both contain token attributes. The query deliberately includes only spans with `gen_ai.usage.input_tokens`.

---

## Bonus: Estimate Projected Usage Carefully

Projecting a short workshop sample over an entire month can produce a misleading result.

If you extend this workflow for a real service:

1. Use a consistent reporting period.
2. Confirm that traffic during that period is representative.
3. Separate weekdays, weekends, and unusual traffic.
4. Include the model identifier in the calculation.
5. Keep prices in a lookup table rather than hardcoding them.
6. Label projected values as estimates.

A simple multiplication of one workshop execution by 30 is not a reliable monthly forecast.

---

## ✅ Checkpoint

Before completing the lab, verify that:

- [ ] You created `AI Usage Monitor - {YOUR_ATTENDEE_ID}`
- [ ] The workflow uses a time interval trigger
- [ ] `get_token_usage` executes successfully
- [ ] The query loads `/lookups/ai/bedrock/model-costs`
- [ ] The query calculates total input and output tokens
- [ ] The query calculates an estimated cost
- [ ] The condition references the result of `get_token_usage`
- [ ] You tested both the true and false condition paths
- [ ] You reviewed the workflow execution details
- [ ] You configured a notification or reviewed why no connection was available

---

## 🆘 Troubleshooting

### The DQL task returns no records

Check:

1. The attendee ID in the query
2. The service name in Dynatrace
3. The workflow query timeframe
4. Whether the application generated recent requests
5. Whether the spans contain `gen_ai.usage.input_tokens`

Run this query in a Notebook:

```dql
fetch spans
| filter service.name == "ai-chat-service-{YOUR_ATTENDEE_ID}"
| filter isNotNull(gen_ai.usage.input_tokens)
| fields
    timestamp,
    span.name,
    gen_ai.response.model,
    gen_ai.usage.input_tokens,
    gen_ai.usage.output_tokens
| sort timestamp desc
| limit 20
```

### The lookup removes every record

The filter:

```dql
| filter isNotNull(pricing.model)
```

removes models that were not matched by the lookup.

Check the recorded model values:

```dql
fetch spans
| filter service.name == "ai-chat-service-{YOUR_ATTENDEE_ID}"
| filter isNotNull(gen_ai.response.model)
| summarize request_count = count(), by: {gen_ai.response.model}
```

Then inspect the lookup:

```dql
load "/lookups/ai/bedrock/model-costs"
```

The value in `gen_ai.response.model` must exist in the lookup table's `model` field.

Expected values include:

```text
workshop-chat
```

and:

```text
us.amazon.nova-micro-v1:0
```

If a different value is recorded, the instructor must add that exact value to the lookup table.

### The lookup table cannot be loaded

Confirm that:

1. The path is exactly:

```text
/lookups/ai/bedrock/model-costs
```

2. Your workshop account has `storage:files:read`.
3. The lookup was uploaded successfully.
4. The table is available in the same Dynatrace environment.

### The condition fails with `records[0]`

The DQL task returned no records.

Run `get_token_usage` independently and resolve the missing-data or lookup issue before evaluating the condition.

### The condition always evaluates to false

Open the output of `get_token_usage` and note the value of:

```text
total_tokens
```

Set the workshop threshold below that value and run the workflow again.

Do not leave an artificially low threshold in a production workflow.

### The notification action is unavailable

The notification connection may not be installed or configured in the workshop environment.

You can still complete the core exercise by:

1. Running the workflow manually
2. Inspecting the DQL task result
3. Confirming the condition result
4. Reviewing which branch would have executed

### The notification task fails

Check:

1. The selected connection
2. The recipient or destination
3. The expression references
4. Whether `get_token_usage` returned a record
5. Whether the workflow action has permission to use the connection

Use the workflow execution details to identify which field failed.

### The notification contains an empty model value

The field name contains dots:

```text
gen_ai.response.model
```

Use bracket notation if the workflow expression editor does not accept dot notation:

{% raw %}

```text
{{ result("get_token_usage").records[0]["gen_ai.response.model"] }}
```

{% endraw %}

### The estimated cost appears as zero

Nova Micro costs are very low, and the workshop produces few tokens. The value may be rounded when displayed.

Inspect the raw `estimated_cost_usd` value or display more decimal places in the notification.

---

## 🎓 What You Have Learned

<div class="persona-box developer" markdown="1">

### 💻 Developer Takeaways

You can now:

1. Automate a DQL query for your AI service
2. Monitor input and output token usage
3. Trigger an action only after a threshold is exceeded
4. Identify operations that consume the most tokens
5. Use workflow execution details to troubleshoot automation

**Practical use:** schedule lightweight checks that highlight unusual growth in prompt size, model output, or request volume.

</div>

<div class="persona-box sre" markdown="1">

### 🔧 SRE and Platform Takeaways

You can now:

1. Enrich telemetry with centrally maintained pricing data
2. Calculate estimated model cost without hardcoding prices
3. Configure conditional workflow execution
4. Connect observability analysis to a notification action
5. Test both positive and negative workflow paths
6. Review workflow evidence before escalating an issue

**Practical use:** turn repeatable AI usage analysis into monitored operational processes.

</div>

---

## 🚀 Take It Further

Ideas for extending the workshop workflow:

| Workflow | Detection | Possible action |
|---|---|---|
| Token usage monitor | Token volume exceeds a reviewed threshold | Notify the service owner |
| Large-prompt monitor | Average input tokens increase | Review prompts and retrieved context |
| Output growth monitor | Average output tokens increase | Review response-length instructions |
| LLM latency monitor | Model-call latency exceeds expectations | Investigate the gateway and provider call |
| Simulated-error summary | Workshop error logs are detected | Send a training summary |
| Weekly usage report | Scheduled reporting period completes | Send usage and cost estimates |
| Lookup validation | An observed model has no pricing match | Notify the lookup-table owner |

These examples require review and adaptation before production use.

---

## 🎉 Lab Complete!

You have created a workflow that retrieves AI telemetry, enriches it with pricing data, evaluates a token threshold, and conditionally runs a notification.

<div class="lab-nav">
  <a href="lab3-dynatrace-mcp">← Lab 3: Dynatrace MCP</a>
  <a href="resources">View Resources →</a>
</div>