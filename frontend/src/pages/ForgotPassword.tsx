import { AuthLayout } from "@/components/auth/AuthLayout";
import { ForgotPasswordForm } from "@/components/auth/ForgotPasswordForm";

const ForgotPassword = () => {
  return (
    <AuthLayout 
      title="Reset your password" 
      subtitle="Enter your email to receive reset instructions"
    >
      <ForgotPasswordForm />
    </AuthLayout>
  );
};

export default ForgotPassword;