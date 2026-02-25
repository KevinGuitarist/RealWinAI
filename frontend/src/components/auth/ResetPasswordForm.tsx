import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Formik, Form, Field, ErrorMessage } from "formik";
import * as Yup from "yup";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useToast } from "@/hooks/use-toast";
import { resetPassword } from "@/lib/auth";

interface ResetPasswordFormProps {
  token: string;
}

interface ResetPasswordValues {
  newPassword: string;
  confirmPassword: string;
}

const validationSchema = Yup.object({
  newPassword: Yup.string()
    .min(8, "Password must be at least 8 characters")
    .required("New password is required"),
  confirmPassword: Yup.string()
    .oneOf([Yup.ref('newPassword')], "Passwords must match")
    .required("Please confirm your password")
});

export function ResetPasswordForm({ token }: ResetPasswordFormProps) {
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const { toast } = useToast();

  const initialValues: ResetPasswordValues = {
    newPassword: "",
    confirmPassword: ""
  };

  const handleSubmit = async (values: ResetPasswordValues) => {
    setIsLoading(true);
    try {
      await resetPassword(token, values.newPassword);
      toast({
        title: "Password reset successful",
        description: "Your password has been updated. Please login with your new password.",
        variant: "default"
      });
      navigate('/login');
    } catch (error) {
      toast({
        title: "Password reset failed",
        description: error instanceof Error ? error.message : "Failed to reset password. Please try again.",
        variant: "destructive"
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Formik
      initialValues={initialValues}
      validationSchema={validationSchema}
      onSubmit={handleSubmit}
    >
      {({ isValid, dirty }) => (
        <Form className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="newPassword">New Password</Label>
            <Field
              as={Input}
              id="newPassword"
              name="newPassword"
              type="password"
              placeholder="Enter new password"
              disabled={isLoading}
            />
            <ErrorMessage 
              name="newPassword" 
              component="div" 
              className="text-sm text-destructive" 
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="confirmPassword">Confirm Password</Label>
            <Field
              as={Input}
              id="confirmPassword"
              name="confirmPassword"
              type="password"
              placeholder="Confirm new password"
              disabled={isLoading}
            />
            <ErrorMessage 
              name="confirmPassword" 
              component="div" 
              className="text-sm text-destructive" 
            />
          </div>

          <Button
            type="submit"
            className="w-full"
            disabled={isLoading || !isValid || !dirty}
          >
            {isLoading ? "Resetting..." : "Reset Password"}
          </Button>
        </Form>
      )}
    </Formik>
  );
}