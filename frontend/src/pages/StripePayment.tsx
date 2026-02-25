import React, { useMemo, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useToast } from "@/hooks/use-toast";
import { config } from "@/lib/config";
import { getAccessToken } from "@/lib/auth";

/**
 * Stripe One‑Time Payment (Checkout) Page
 * -------------------------------------------------------------
 * - Redirects to Stripe Checkout in `mode="payment"` for a single charge
 * - Apple Pay / Google Pay supported automatically by Checkout
 * - Backend endpoint expected: POST /subscriptions/stripe/start -> { checkout_url }
 * - Minimal form: name + email (prefill) + optional note/metadata
 *
 * Usage:
 *   <StripeOneTimePaymentPage />
 *
 * You can pass "defaultEmail" and "defaultName" if you have them.
 */

interface Props {
  defaultEmail?: string;
  defaultName?: string;
  buttonText?: string;
}

export default function StripeOneTimePaymentPage({
  defaultEmail,
  defaultName,
  buttonText = "Pay £1"
}: Props) {
  const { toast } = useToast?.() || { toast: (args: any) => console.log(args) };

  const [email, setEmail] = useState(defaultEmail || "");
  const [name, setName] = useState(defaultName || "");
  const [note, setNote] = useState("");
  const [loading, setLoading] = useState(false);

  const disabled = useMemo(() => {
    return loading || !email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }, [email, loading]);

  async function startCheckout() {
    try {
      setLoading(true);
      const token = getAccessToken();
      
      // HITS BACKEND: create a Checkout Session in mode="payment"
      const res = await fetch(`${config.API_BASE_URL}/subscriptions/stripe/start`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ email, full_name: name, note }),
      });

      if (!res.ok) {
        const err = await safeJson(res);
        throw new Error(err?.detail || err?.message || `HTTP ${res.status}`);
      }

      const data: { checkout_url: string } = await res.json();
      if (!data?.checkout_url) throw new Error("No checkout_url returned");

      // Hard redirect to Stripe Checkout
      window.location.href = data.checkout_url;
    } catch (error: any) {
      console.error(error);
      toast({
        title: "Couldn't start payment",
        description: error?.message || "Please try again.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-md p-4">
      <Card className="shadow-lg">
        <CardHeader>
          <CardTitle className="text-xl">One‑time Payment</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="name">Full name</Label>
            <Input
              id="name"
              placeholder="Jane Doe"
              value={name}
              onChange={(e) => setName(e.target.value)}
              autoComplete="name"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              placeholder="jane@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="email"
              required
            />
            <p className="text-xs text-muted-foreground">
              We'll send the Stripe receipt to this email.
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="note">Note (optional)</Label>
            <Input
              id="note"
              placeholder="Any extra info (optional)"
              value={note}
              onChange={(e) => setNote(e.target.value)}
            />
          </div>

          <Button onClick={startCheckout} disabled={disabled} className="w-full h-11">
            {loading ? "Redirecting…" : buttonText}
          </Button>

          <div className="text-xs text-center text-muted-foreground">
            Secured by Stripe • Apple Pay / Google Pay available when supported
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

async function safeJson(res: Response) {
  try { return await res.json(); } catch { return null; }
}