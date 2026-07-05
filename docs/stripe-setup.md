# Stripe Setup

## Products and Prices

Create recurring subscription products or prices for:

- Starter
- Professional
- Growth
- Enterprise

Store price IDs in:

- `STRIPE_STARTER_PRICE_ID`
- `STRIPE_PROFESSIONAL_PRICE_ID`
- `STRIPE_GROWTH_PRICE_ID`
- `STRIPE_ENTERPRISE_PRICE_ID`

## Trial

Set:

```env
STRIPE_TRIAL_DAYS=14
```

Checkout sessions are created in subscription mode and include subscription trial settings. Stripe's current free-trial Checkout guidance is documented at `https://docs.stripe.com/payments/checkout/free-trials`.

## Webhooks Required Before Production

Add and verify these events:

- `checkout.session.completed`
- `customer.subscription.created`
- `customer.subscription.updated`
- `customer.subscription.deleted`
- `invoice.payment_failed`
- `trial_will_end`

Webhook processing should update:

- `stripe_customer_id`
- `stripe_subscription_id`
- `plan`
- `trial_end`
- `subscription_status`
- `usage_limits`

