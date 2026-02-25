import React, { useEffect, useState } from "react";
import { getMySubscription, cancelMySubscription } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/hooks/use-toast";
import { Loader2, Calendar, CreditCard, AlertTriangle } from "lucide-react";

export default function SubscriptionStatus() {
  const [loading, setLoading] = useState(true);
  const [sub, setSub] = useState<any>(null);
  const [msg, setMsg] = useState<string | null>(null);
  const [cancelling, setCancelling] = useState(false);
  const { toast } = useToast();

  async function load() {
    setLoading(true);
    try {
      const s = await getMySubscription();
      setSub(s);
      setMsg(null);
    } catch (e: any) {
      setMsg(e?.message || "No subscription found");
      setSub(null);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function cancel() {
    setCancelling(true);
    try {
      await cancelMySubscription();
      setMsg("Subscription cancelled.");
      toast({
        title: "Subscription Cancelled",
        description: "Your subscription has been cancelled successfully.",
      });
      await load();
    } catch (e: any) {
      const errorMsg = e?.message || "Failed to cancel.";
      setMsg(errorMsg);
      toast({
        variant: "destructive",
        title: "Cancellation Failed",
        description: errorMsg,
      });
    } finally {
      setCancelling(false);
    }
  }

  if (loading) {
    return (
      <Card className="max-w-md mx-auto">
        <CardContent className="p-6">
          <div className="flex items-center justify-center space-x-2">
            <Loader2 className="w-4 h-4 animate-spin" />
            <span>Loading subscription…</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!sub) {
    return (
      <Card className="max-w-md mx-auto">
        <CardContent className="p-6">
          <div className="text-center space-y-4">
            <AlertTriangle className="w-12 h-12 text-muted-foreground mx-auto" />
            <div>
              <h3 className="font-semibold text-foreground">No Subscription Found</h3>
              <p className="text-sm text-muted-foreground">
                {msg || "You don't have an active subscription yet."}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="max-w-md mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Subscription Status</span>
          <Badge variant={sub.is_active ? "default" : "secondary"}>
            {sub.is_active ? "Active" : sub.status}
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-3">
          <div className="flex items-center space-x-2">
            <CreditCard className="w-4 h-4 text-muted-foreground" />
            <div>
              <p className="text-sm font-medium">Plan Status</p>
              <p className="text-sm text-muted-foreground">
                {sub.is_active ? "Premium Subscription" : "Inactive"}
              </p>
            </div>
          </div>

          {sub.next_billing_at && (
            <div className="flex items-center space-x-2">
              <Calendar className="w-4 h-4 text-muted-foreground" />
              <div>
                <p className="text-sm font-medium">Next Billing</p>
                <p className="text-sm text-muted-foreground">
                  {new Date(sub.next_billing_at).toLocaleDateString("en-GB", {
                    year: "numeric",
                    month: "long",
                    day: "numeric",
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </p>
              </div>
            </div>
          )}

          {sub.email && (
            <div className="bg-surface/50 rounded-lg p-3">
              <p className="text-sm font-medium">Account Email</p>
              <p className="text-sm text-muted-foreground">{sub.email}</p>
            </div>
          )}
        </div>

        {sub.is_active && (
          <Button
            onClick={cancel}
            disabled={cancelling}
            variant="destructive"
            className="w-full"
          >
            {cancelling ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Cancelling...
              </>
            ) : (
              "Cancel Subscription"
            )}
          </Button>
        )}

        {msg && (
          <div className="text-sm text-muted-foreground text-center bg-surface/50 rounded-lg p-3">
            {msg}
          </div>
        )}
      </CardContent>
    </Card>
  );
}