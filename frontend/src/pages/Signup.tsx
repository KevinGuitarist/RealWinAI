import { AuthLayout } from "@/components/auth/AuthLayout";
import { SignupForm } from "@/components/auth/SignupForm";

const Signup = () => {
  return (
    <AuthLayout 
      title="Create your account" 
      subtitle="Join RealWin.AI for advanced sports predictions"
    >
      <SignupForm />
    </AuthLayout>
  );
};

export default Signup;