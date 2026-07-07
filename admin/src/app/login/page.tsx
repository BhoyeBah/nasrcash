import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { LoginForm } from "@/components/login-form";

export default function LoginPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4">
      <div className="w-full max-w-sm">
        <div className="mb-6 text-center">
          <p className="text-xl font-semibold tracking-tight text-primary">NasrCash</p>
          <p className="text-sm text-muted-foreground">Back-office administrateur</p>
        </div>
        <Card>
          <CardHeader>
            <CardTitle className="text-base font-semibold text-foreground">
              Connexion
            </CardTitle>
          </CardHeader>
          <CardContent>
            <LoginForm />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
