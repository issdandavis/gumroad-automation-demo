import { useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useLocation } from "wouter";
import Layout from "@/components/dashboard/Layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Loader2, Users, Building2, Coins, DollarSign, Trash2 } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface AdminUser {
  id: string;
  email: string;
  role: string;
  createdAt: string;
  orgs: { id: string; name: string }[];
}

interface AdminStats {
  totalUsers: number;
  totalOrgs: number;
  totalTokens: number;
  totalCostUsd: number;
}

interface CurrentUser {
  id: string;
  email: string;
  role: string;
}

export default function Admin() {
  const [, navigate] = useLocation();
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const { data: currentUser, isLoading: loadingUser } = useQuery<CurrentUser>({
    queryKey: ["/api/auth/me"],
    queryFn: async () => {
      const res = await fetch("/api/auth/me");
      if (!res.ok) throw new Error("Not authenticated");
      return res.json();
    },
  });

  const { data: users, isLoading: loadingUsers } = useQuery<AdminUser[]>({
    queryKey: ["/api/admin/users"],
    queryFn: async () => {
      const res = await fetch("/api/admin/users");
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.error || "Failed to fetch users");
      }
      return res.json();
    },
    enabled: !!currentUser && (currentUser.role === "owner" || currentUser.role === "admin"),
  });

  const { data: stats, isLoading: loadingStats } = useQuery<AdminStats>({
    queryKey: ["/api/admin/stats"],
    queryFn: async () => {
      const res = await fetch("/api/admin/stats");
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.error || "Failed to fetch stats");
      }
      return res.json();
    },
    enabled: !!currentUser && (currentUser.role === "owner" || currentUser.role === "admin"),
  });

  const deleteUserMutation = useMutation({
    mutationFn: async (userId: string) => {
      const res = await fetch(`/api/admin/users/${userId}`, { method: "DELETE" });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.error || "Failed to delete user");
      }
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/admin/users"] });
      queryClient.invalidateQueries({ queryKey: ["/api/admin/stats"] });
      toast({ title: "User deleted successfully" });
    },
    onError: (error: Error) => {
      toast({ title: "Error", description: error.message, variant: "destructive" });
    },
  });

  useEffect(() => {
    if (!loadingUser && currentUser && currentUser.role !== "owner" && currentUser.role !== "admin") {
      navigate("/dashboard");
    }
  }, [currentUser, loadingUser, navigate]);

  const handleDeleteUser = (user: AdminUser) => {
    if (user.id === currentUser?.id) {
      toast({ title: "Error", description: "Cannot delete yourself", variant: "destructive" });
      return;
    }
    if (confirm(`Are you sure you want to delete user "${user.email}"? This will also delete their organizations.`)) {
      deleteUserMutation.mutate(user.id);
    }
  };

  if (loadingUser) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-64">
          <Loader2 className="w-8 h-8 animate-spin" />
        </div>
      </Layout>
    );
  }

  if (!currentUser || (currentUser.role !== "owner" && currentUser.role !== "admin")) {
    return null;
  }

  return (
    <Layout>
      <div className="space-y-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight mb-2 text-glow" data-testid="text-admin-title">
            Super Admin Dashboard
          </h1>
          <p className="text-muted-foreground">
            Manage users, view global statistics, and monitor system health.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card className="glass-panel" data-testid="card-total-users">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Users</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold" data-testid="text-total-users">
                {loadingStats ? "..." : stats?.totalUsers || 0}
              </div>
            </CardContent>
          </Card>

          <Card className="glass-panel" data-testid="card-total-orgs">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Organizations</CardTitle>
              <Building2 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold" data-testid="text-total-orgs">
                {loadingStats ? "..." : stats?.totalOrgs || 0}
              </div>
            </CardContent>
          </Card>

          <Card className="glass-panel" data-testid="card-total-tokens">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Tokens (30d)</CardTitle>
              <Coins className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold" data-testid="text-total-tokens">
                {loadingStats ? "..." : (stats?.totalTokens || 0).toLocaleString()}
              </div>
            </CardContent>
          </Card>

          <Card className="glass-panel" data-testid="card-total-cost">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Cost (30d)</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold" data-testid="text-total-cost">
                ${loadingStats ? "..." : (stats?.totalCostUsd || 0).toFixed(4)}
              </div>
            </CardContent>
          </Card>
        </div>

        <Card className="glass-panel">
          <CardHeader>
            <CardTitle>All Users</CardTitle>
          </CardHeader>
          <CardContent>
            {loadingUsers ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="w-6 h-6 animate-spin" />
              </div>
            ) : (
              <Table data-testid="table-users">
                <TableHeader>
                  <TableRow>
                    <TableHead>Email</TableHead>
                    <TableHead>Role</TableHead>
                    <TableHead>Organizations</TableHead>
                    <TableHead>Created</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {users?.map((user) => (
                    <TableRow key={user.id} data-testid={`row-user-${user.id}`}>
                      <TableCell data-testid={`text-email-${user.id}`}>{user.email}</TableCell>
                      <TableCell>
                        <Badge variant={user.role === "owner" ? "default" : "secondary"} data-testid={`badge-role-${user.id}`}>
                          {user.role}
                        </Badge>
                      </TableCell>
                      <TableCell data-testid={`text-orgs-${user.id}`}>
                        {user.orgs.length > 0 ? user.orgs.map(o => o.name).join(", ") : "None"}
                      </TableCell>
                      <TableCell data-testid={`text-created-${user.id}`}>
                        {new Date(user.createdAt).toLocaleDateString()}
                      </TableCell>
                      <TableCell className="text-right">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDeleteUser(user)}
                          disabled={deleteUserMutation.isPending || user.id === currentUser?.id}
                          data-testid={`button-delete-${user.id}`}
                        >
                          <Trash2 className="h-4 w-4 text-destructive" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                  {(!users || users.length === 0) && (
                    <TableRow>
                      <TableCell colSpan={5} className="text-center text-muted-foreground py-8">
                        No users found
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
      </div>
    </Layout>
  );
}
