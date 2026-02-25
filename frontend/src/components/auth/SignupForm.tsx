import { useState, useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { Formik, Form, Field, ErrorMessage } from "formik";
import * as Yup from "yup";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useToast } from "@/hooks/use-toast";
import { Eye, EyeOff } from "lucide-react";
import { signupUser, saveAuthTokens } from "@/lib/auth";

const validationSchema = Yup.object({
  firstName: Yup.string()
    .min(2, 'First name must be at least 2 characters')
    .required('First name is required'),
  lastName: Yup.string()
    .min(2, 'Last name must be at least 2 characters')
    .required('Last name is required'),
  email: Yup.string()
    .email('Invalid email address')
    .required('Email is required'),
  password: Yup.string()
    .min(6, 'Password must be at least 6 characters')
    .required('Password is required'),
  confirmPassword: Yup.string()
    .oneOf([Yup.ref('password')], 'Passwords must match')
    .required('Please confirm your password'),
});

export function SignupForm() {
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [source, setSource] = useState<string>("");
  const { toast } = useToast();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  // Capture source from URL params or referrer
  useEffect(() => {
    const sourceParam = searchParams.get('source');
    const referrer = document.referrer;
    
    if (sourceParam) {
      setSource(sourceParam);
    } else if (referrer) {
      // Extract domain from referrer
      try {
        const referrerDomain = new URL(referrer).hostname;
        if (referrerDomain.includes('google')) {
          setSource('google');
        } else if (referrerDomain.includes('facebook')) {
          setSource('facebook');
        } else if (referrerDomain.includes('x.com')) {
          setSource('x');
        } else if (referrerDomain.includes('linkedin')) {
          setSource('linkedin');
        } else {
          setSource(referrerDomain);
        }
      } catch (error) {
        setSource('direct');
      }
    } else {
      setSource('direct');
    }
  }, [searchParams]);

  const initialValues = {
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    confirmPassword: '',
  };

  const handleSubmit = async (values: typeof initialValues, { setSubmitting }: any) => {
    try {
      const signupData = {
        email: values.email,
        password: values.password,
        first_name: values.firstName,
        last_name: values.lastName,
        source: source,
      };

      const response = await signupUser(signupData);
      saveAuthTokens(response);
      
      // Set flag to indicate user just signed up
      sessionStorage.setItem('just_signed_up', '1');
      
      toast({
        title: "🎉 Account Created Successfully!",
        description: "Welcome to RealWin.AI! Redirecting to your dashboard...",
        className: "bg-gradient-to-r from-green-50 to-emerald-50 border-green-200 text-green-800",
      });
      
      setTimeout(() => {
        navigate('/dashboard');
      }, 1500);
    } catch (error) {
      toast({
        title: "❌ Signup Failed",
        description: error instanceof Error ? error.message : "Something went wrong. Please try again.",
        variant: "destructive",
        className: "bg-gradient-to-r from-red-50 to-rose-50 border-red-200 text-red-800",
      });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Formik
      initialValues={initialValues}
      validationSchema={validationSchema}
      onSubmit={handleSubmit}
    >
      {({ isSubmitting, errors, touched }) => (
        <Form className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="firstName">First Name</Label>
              <Field
                as={Input}
                id="firstName"
                name="firstName"
                type="text"
                placeholder="John"
                className={`bg-input border-border ${
                  errors.firstName && touched.firstName ? 'border-destructive' : ''
                }`}
              />
              <ErrorMessage 
                name="firstName" 
                component="div" 
                className="text-sm text-destructive"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="lastName">Last Name</Label>
              <Field
                as={Input}
                id="lastName"
                name="lastName"
                type="text"
                placeholder="Doe"
                className={`bg-input border-border ${
                  errors.lastName && touched.lastName ? 'border-destructive' : ''
                }`}
              />
              <ErrorMessage 
                name="lastName" 
                component="div" 
                className="text-sm text-destructive"
              />
            </div>
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Field
              as={Input}
              id="email"
              name="email"
              type="email"
              placeholder="john@example.com"
              className={`bg-input border-border ${
                errors.email && touched.email ? 'border-destructive' : ''
              }`}
            />
            <ErrorMessage 
              name="email" 
              component="div" 
              className="text-sm text-destructive"
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="password">Password</Label>
            <div className="relative">
              <Field
                as={Input}
                id="password"
                name="password"
                type={showPassword ? "text" : "password"}
                placeholder="Create a strong password"
                className={`bg-input border-border pr-10 ${
                  errors.password && touched.password ? 'border-destructive' : ''
                }`}
              />
              <Button
                type="button"
                variant="ghost"
                size="sm"
                className="absolute right-0 top-0 h-full px-3"
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? (
                  <EyeOff className="h-4 w-4" />
                ) : (
                  <Eye className="h-4 w-4" />
                )}
              </Button>
            </div>
            <ErrorMessage 
              name="password" 
              component="div" 
              className="text-sm text-destructive"
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="confirmPassword">Confirm Password</Label>
            <div className="relative">
              <Field
                as={Input}
                id="confirmPassword"
                name="confirmPassword"
                type={showConfirmPassword ? "text" : "password"}
                placeholder="Confirm your password"
                className={`bg-input border-border pr-10 ${
                  errors.confirmPassword && touched.confirmPassword ? 'border-destructive' : ''
                }`}
              />
              <Button
                type="button"
                variant="ghost"
                size="sm"
                className="absolute right-0 top-0 h-full px-3"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
              >
                {showConfirmPassword ? (
                  <EyeOff className="h-4 w-4" />
                ) : (
                  <Eye className="h-4 w-4" />
                )}
              </Button>
            </div>
            <ErrorMessage 
              name="confirmPassword" 
              component="div" 
              className="text-sm text-destructive"
            />
          </div>
          
          <Button 
            type="submit" 
            className="w-full gradient-brand hover:opacity-90 transition-opacity" 
            disabled={isSubmitting}
          >
            {isSubmitting ? "Creating account..." : "Create Account"}
          </Button>
          
          <div className="text-center text-sm text-muted-foreground">
            Already have an account?{" "}
            <a href="/login" className="text-brand-accent hover:underline">
              Sign in
            </a>
          </div>
        </Form>
      )}
    </Formik>
  );
}