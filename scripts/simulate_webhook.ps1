param(
    [ValidateSet("invoice.created", "invoice.updated", "payment.created", "bill.created", "creditnote.created", "purchaseorder.created")]
    [string]$Event = "invoice.created",
    [string]$Url = "http://127.0.0.1:8080/webhook/zoho",
    [string]$Token = $env:ZOHO_WEBHOOK_TOKEN
)

$ErrorActionPreference = "Stop"

$payloads = @{
    "invoice.created" = @{
        event = "invoice.created"
        organization_id = "org-test-123"
        data = @{
            invoice = @{
                invoice_id = "inv-sim-001"
                invoice_number = "INV-SIM-001"
                customer_name = "Simulated Customer"
                total = 1500.00
                currency_code = "USD"
                date = "2026-06-13"
                due_date = "2026-07-13"
                status = "draft"
            }
        }
    }
}

if (-not $payloads.ContainsKey($Event)) {
    Write-Error "Payload for $Event not defined in simulate script yet."
}

$body = $payloads[$Event] | ConvertTo-Json -Depth 6
$headers = @{ "Content-Type" = "application/json" }
if ($Token) {
    $headers["X-Zoho-Webhook-Token"] = $Token
}

Write-Host "POST $Url event=$Event"
$response = Invoke-WebRequest -Uri $Url -Method POST -Body $body -Headers $headers -UseBasicParsing
Write-Host "Status:" $response.StatusCode
Write-Host $response.Content
