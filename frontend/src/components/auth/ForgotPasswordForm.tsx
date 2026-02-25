import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useToast } from "@/hooks/use-toast";
import { Formik, Form, Field, ErrorMessage } from "formik";
import * as Yup from "yup";
import { forgotPassword } from "@/lib/auth";

const validationSchema = Yup.object({
  email: Yup.string()
    .email("Please enter a valid email address")
    .required("Email is required"),
});

export function ForgotPasswordForm() {
  const [isSubmitted, setIsSubmitted] = useState(false);
  const { toast } = useToast();

  const handleSubmit = async (values: { email: string }, { setSubmitting }: any) => {
    try {
      await forgotPassword(values.email);
      setIsSubmitted(true);
      toast({
        title: "Reset instructions sent",
        description: "If an account exists, you'll get email to reset password.",
      });
    } catch (error) {
      // Always show success message for security reasons
      setIsSubmitted(true);
      toast({
        title: "Reset instructions sent", 
        description: "If an account exists, you'll get email to reset password.",
      });
    } finally {
      setSubmitting(false);
    }
  };

  if (isSubmitted) {
    return (
      <div className="text-center space-y-4">
        <div className="w-12 h-12 bg-brand-primary rounded-full flex items-center justify-center mx-auto">
          <svg
            className="w-6 h-6 text-black"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M5 13l4 4L19 7"
            />
          </svg>
        </div>
        <div>
          <h3 className="text-lg font-semibold text-foreground">Check your email</h3>
          <p className="text-muted-foreground mt-2">
            If an account exists, you'll get email to reset password.
          </p>
        </div>
        <div className="space-y-2">
          <Button
            onClick={() => setIsSubmitted(false)}
            variant="outline"
            className="w-full"
          >
            Try another email
          </Button>
          <a 
            href="/login" 
            className="block text-sm text-brand-accent hover:underline"
          >
            Back to login
          </a>
        </div>
      </div>
    );
  }

  return (
    <Formik
      initialValues={{ email: "" }}
      validationSchema={validationSchema}
      onSubmit={handleSubmit}
    >
      {({ isSubmitting, errors, touched }) => (
        <Form className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="email">Email Address</Label>
            <Field
              as={Input}
              id="email"
              name="email"
              type="email"
              placeholder="Enter your email address"
              className="bg-input border-border"
            />
            <ErrorMessage 
              name="email" 
              component="p" 
              className="text-xs text-destructive" 
            />
            <p className="text-xs text-muted-foreground">
              We'll send you a link to reset your password.
            </p>
          </div>
          
          <Button 
            type="submit" 
            className="w-full gradient-brand hover:opacity-90 transition-opacity" 
            disabled={isSubmitting}
          >
            {isSubmitting ? "Sending..." : "Send Reset Link"}
          </Button>
          
          <div className="text-center">
            <a 
              href="/login" 
              className="text-sm text-brand-accent hover:underline"
            >
              Back to login
            </a>
          </div>
        </Form>
      )}
    </Formik>
  );
}