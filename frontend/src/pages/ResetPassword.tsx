import { useEffect } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { AuthLayout } from "@/components/auth/AuthLayout";
import { ResetPasswordForm } from "@/components/auth/ResetPasswordForm";

const ResetPassword = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const token = searchParams.get('token');

  useEffect(() => {
    if (!token) {
      navigate('/forgot-password');
    }
  }, [token, navigate]);

  if (!token) {
    return null;
  }

  return (
    <AuthLayout 
      title="Reset your password" 
      subtitle="Enter your new password below"
    >
      <ResetPasswordForm token={token} />
    </AuthLayout>
  );
};

export default ResetPassword;