import { useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { CheckCircle } from "lucide-react";
import { useNavigate } from "react-router-dom";

const PaymentSuccess = () => {
  const navigate = useNavigate();

  useEffect(() => {
    // Set page title for SEO
    document.title = "Payment Successful - RealWin";
  }, []);

  const handleGoToDashboard = () => {
    sessionStorage.setItem('just_paid', '1');
    navigate("/dashboard");
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <Card className="max-w-md w-full">
        <CardContent className="p-8 text-center space-y-6">
          {/* Success Icon */}
          <div className="flex justify-center">
            <div className="rounded-full bg-green-100 p-4">
              <CheckCircle className="h-12 w-12 text-green-600" />
            </div>
          </div>

          {/* Success Message */}
          <div className="space-y-2">
            <h1 className="text-2xl font-bold text-foreground">Payment Successful!</h1>
            <p className="text-muted-foreground">
              Thank you for your payment. Your subscription is now active and you have full access to all premium features.
            </p>
          </div>


          {/* Dashboard Button */}
          <Button 
            onClick={handleGoToDashboard}
            className="w-full bg-brand-primary hover:bg-brand-primary-hover"
            size="lg"
          >
            Go to Dashboard
          </Button>

        </CardContent>
      </Card>
    </div>
  );
};

export default PaymentSuccess;