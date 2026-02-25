import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useToast } from "@/hooks/use-toast";
import { Eye, EyeOff } from "lucide-react";
import { useFormik } from "formik";
import * as Yup from "yup";
import { loginUser, saveAuthTokens } from "@/lib/auth";

const validationSchema = Yup.object({
  email: Yup.string()
    .email("Invalid email address")
    .required("Email is required"),
  password: Yup.string()
    .min(6, "Password must be at least 6 characters")
    .required("Password is required"),
});

export function LoginForm() {
  const [showPassword, setShowPassword] = useState(false);
  const { toast } = useToast();

  const formik = useFormik({
    initialValues: {
      email: "",
      password: "",
    },
    validationSchema,
    onSubmit: async (values) => {
      try {
        const response = await loginUser(values);
        saveAuthTokens(response);
        toast({
          title: "🎉 Welcome back!",
          description: "You've successfully signed in to RealWin.AI",
          className: "bg-gradient-to-r from-green-50 to-emerald-50 border-green-200 text-green-800",
        });
        setTimeout(() => {
          window.location.href = "/dashboard";
        }, 1000);
      } catch (error) {
        toast({
          title: "❌ Login Failed",
          description: "Incorrect email or password. Please check your credentials and try again.",
          variant: "destructive",
          className: "bg-gradient-to-r from-red-50 to-rose-50 border-red-200 text-red-800",
        });
      }
    },
  });

  return (
    <form onSubmit={formik.handleSubmit} className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="email">Email</Label>
        <Input
          id="email"
          name="email"
          type="email"
          placeholder="Enter your email"
          value={formik.values.email}
          onChange={formik.handleChange}
          onBlur={formik.handleBlur}
          className="bg-input border-border"
        />
        {formik.touched.email && formik.errors.email && (
          <p className="text-sm text-destructive">{formik.errors.email}</p>
        )}
      </div>
      
      <div className="space-y-2">
        <Label htmlFor="password">Password</Label>
        <div className="relative">
          <Input
            id="password"
            name="password"
            type={showPassword ? "text" : "password"}
            placeholder="Enter your password"
            value={formik.values.password}
            onChange={formik.handleChange}
            onBlur={formik.handleBlur}
            className="bg-input border-border pr-10"
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
        {formik.touched.password && formik.errors.password && (
          <p className="text-sm text-destructive">{formik.errors.password}</p>
        )}
      </div>
      
      <Button 
        type="submit" 
        className="w-full gradient-brand hover:opacity-90 transition-opacity" 
        disabled={formik.isSubmitting}
      >
        {formik.isSubmitting ? "Signing in..." : "Sign In"}
      </Button>
      
      <div className="text-center space-y-2">
        <a 
          href="/forgot-password" 
          className="text-sm text-brand-accent hover:underline"
        >
          Forgot your password?
        </a>
        <div className="text-sm text-muted-foreground">
          Don't have an account?{" "}
          <a href="/signup" className="text-brand-accent hover:underline">
            Sign up
          </a>
        </div>
      </div>
    </form>
  );
}