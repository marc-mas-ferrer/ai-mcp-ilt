---
title: Grail and DQL
topic: dql
---

## Grail

Grail is the Dynatrace data lakehouse. It stores logs, traces, metrics, events and business events together in one place, with no indexes and no schema defined up front, so data keeps its full context and can be queried as it was ingested. Grail is the storage layer that DQL queries read from, and it also holds lookup tables that queries can join against.

## DQL basics

DQL, the Dynatrace Query Language, queries data stored in Grail. A query names a data source, then pipes records through commands. Example:
fetch logs
| filter loglevel == "ERROR"
| summarize error_count = count(), by:{host.name}
| sort error_count desc
| limit 10
Read it top to bottom: fetch logs, keep error records, count per host, sort, return ten rows.

## DQL commands

Common DQL commands are fetch to choose a data source such as logs, spans, events or metrics; filter to keep matching records; fields and fieldsAdd to select or calculate columns; summarize to aggregate with functions like count, sum, avg and max; sort and limit to order and trim the result; lookup to enrich records from a lookup table; and makeTimeseries to turn records into a time series for charting. They combine like this:
fetch logs | filter loglevel == "ERROR" | summarize count(), by:{host.name}

## DQL syntax rules

In DQL, comparison uses a double equals sign and string values are written in double quotes, for example filter service.name == "checkout". Aggregates in summarize are given a name, as in total_tokens = sum(gen_ai.usage.input_tokens). Grouping is written as by:{field}. Field names that contain dots are written as-is and do not need quoting.
