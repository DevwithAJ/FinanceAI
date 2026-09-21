# FinanceAI 2.0 API Documentation

The JSON API is intended for educational integration and testing. Browser session authentication is required where stated.

## GET `/api/v1/status`

Returns FinanceAI application/module status and the current build version.

## POST `/api/v1/personal-finance`

Accepts Personal Finance input and returns the Financial Health result and recommendations.

## GET `/api/v1/credit-stress/schema`

Returns the Credit Stress input schema and model metadata intended for the UI.

## POST `/api/v1/credit-stress`

Runs the experimental Credit Stress model.

## GET `/api/v1/loan-risk/schema`

Returns the Loan Risk form/schema metadata.

## POST `/api/v1/loan-risk`

Runs the experimental Loan Risk model.

## GET `/api/v1/history`

Login required. Returns saved analysis history for the current user.

## GET `/api/v1/transactions`

Login required. Returns the current user's transaction data.

## GET `/api/v1/forecast`

Login required. Returns the current user's 30/60/90-day cash-flow forecast.

## GET `/api/v1/spending-insights`

Login required. Returns spending-behavior and anomaly-detection results.

## GET `/api/v1/net-worth`

Login required. Returns the current user's net-worth summary.

## GET `/version`

Returns the exact application build identifier (`2.0.0`) and the local assistant mode. It does not expose local filesystem paths or secrets.

> Risk and forecast endpoints provide educational analytics, not official lending or professional financial decisions.
