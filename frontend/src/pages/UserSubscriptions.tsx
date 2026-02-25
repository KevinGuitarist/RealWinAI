import { useState, useEffect } from "react";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { Eye, Search, ChevronLeft, ChevronRight, Download } from "lucide-react";
import { getUsersSubscriptions } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";
import { format } from "date-fns";

interface UserSubscription {
  first_name: string;
  last_name: string;
  email: string;
  create_date: string;
  subscription_date: string | null;
  payment_method_id: string | null;
  payment_method_type: string | null;
  status: string | null;
  next_billing_at: string | null;
  last_order_id: string | null;
  last_login_ip: string | null;
  last_seen_at: string | null;
  geo_country: string | null;
  geo_region: string | null;
  geo_city: string | null;
  geo_latitude: number | null;
  geo_longitude: number | null;
  source: string | null;
}

interface ApiResponse {
  count: number;
  limit: number;
  offset: number;
  order_by: string;
  order_dir: string;
  results: UserSubscription[];
}

const UserSubscriptions = () => {
  const [data, setData] = useState<ApiResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [exportLoading, setExportLoading] = useState(false);
  const [selectedUser, setSelectedUser] = useState<UserSubscription | null>(null);
  const [filters, setFilters] = useState({
    status: "all_statuses",
    email: "",
    page: 0,
    limit: 50,
    order_by: "user_create_date",
    order_dir: "desc"
  });
  const { toast } = useToast();

  const fetchData = async () => {
    try {
      setLoading(true);
      const response = await getUsersSubscriptions({
        limit: filters.limit,
        offset: filters.page * filters.limit,
        status: filters.status !== "all_statuses" ? filters.status : undefined,
        email: filters.email || undefined,
        order_by: filters.order_by,
        order_dir: filters.order_dir
      });
      setData(response);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to fetch user subscriptions",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [filters]);

  const formatDate = (dateString: string | null) => {
    if (!dateString) return "N/A";
    return format(new Date(dateString), "MMM dd, yyyy HH:mm");
  };

  const getStatusBadge = (status: string | null) => {
    if (!status) return <Badge variant="secondary">No Subscription</Badge>;
    
    switch (status) {
      case "active":
        return <Badge variant="default" className="bg-green-500">Active</Badge>;
      case "canceled":
        return <Badge variant="destructive">Canceled</Badge>;
      case "pending_initial_payment":
        return <Badge variant="secondary" className="bg-yellow-500">Pending Payment</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  const handleSearch = () => {
    setFilters(prev => ({ ...prev, page: 0 }));
  };

  const handlePageChange = (newPage: number) => {
    setFilters(prev => ({ ...prev, page: newPage }));
  };

  const exportToCSV = async () => {
    if (exportLoading) return;
    
    try {
      setExportLoading(true);
      
      toast({
        title: "Export Started",
        description: "Fetching all records for CSV export...",
      });

      // Use the count from current data to fetch ALL records
      const totalCount = data?.count || 0;
      if (totalCount === 0) {
        toast({
          title: "No Data",
          description: "No records available to export",
          variant: "destructive"
        });
        return;
      }

      // Fetch ALL records in batches since API might have limit restrictions
      const batchSize = 100; // Safe batch size
      const allResults: UserSubscription[] = [];
      
      for (let offset = 0; offset < totalCount; offset += batchSize) {
        const batchData = await getUsersSubscriptions({
          limit: Math.min(batchSize, totalCount - offset),
          offset: offset,
          status: filters.status !== "all_statuses" ? filters.status : undefined,
          email: filters.email || undefined,
          order_by: filters.order_by,
          order_dir: filters.order_dir
        });
        
        if (batchData && batchData.results) {
          allResults.push(...batchData.results);
        }
      }

      if (allResults.length === 0) {
        toast({
          title: "No Data",
          description: "No records found to export",
          variant: "destructive"
        });
        return;
      }

      // Create CSV headers
      const headers = [
        "First Name",
        "Last Name", 
        "Email",
        "Create Date",
        "Subscription Date",
        "Status",
        "Payment Method",
        "Next Billing",
        "Last Order ID",
        "Last Login IP",
        "Last Seen",
        "Source",
        "Country",
        "Region",
        "City",
        "Latitude",
        "Longitude"
      ];

      // Create CSV rows
      const csvRows = [headers.join(",")];
      
      allResults.forEach((user: UserSubscription) => {
        const row = [
          `"${user.first_name || ''}"`,
          `"${user.last_name || ''}"`,
          `"${user.email || ''}"`,
          `"${user.create_date || ''}"`,
          `"${user.subscription_date || 'N/A'}"`,
          `"${user.status || 'No Subscription'}"`,
          `"${user.payment_method_type || 'N/A'}"`,
          `"${user.next_billing_at || 'N/A'}"`,
          `"${user.last_order_id || 'N/A'}"`,
          `"${user.last_login_ip || 'N/A'}"`,
          `"${user.last_seen_at || 'N/A'}"`,
          `"${user.source || 'N/A'}"`,
          `"${user.geo_country || 'N/A'}"`,
          `"${user.geo_region || 'N/A'}"`,
          `"${user.geo_city || 'N/A'}"`,
          `"${user.geo_latitude || 'N/A'}"`,
          `"${user.geo_longitude || 'N/A'}"`
        ];
        csvRows.push(row.join(","));
      });

      const csvContent = csvRows.join("\n");

      // Create and download file
      const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
      const url = URL.createObjectURL(blob);
      
      const link = document.createElement("a");
      link.href = url;
      link.download = `user_subscriptions_all_${new Date().toISOString().split('T')[0]}.csv`;
      link.style.display = "none";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);

      toast({
        title: "Export Successful",
        description: `Exported ${allResults.length} total records to CSV`,
      });

    } catch (error) {
      console.error("Export error:", error);
      toast({
        title: "Export Failed",
        description: `Error: ${error instanceof Error ? error.message : 'Failed to export CSV'}`,
        variant: "destructive"
      });
    } finally {
      setExportLoading(false);
    }
  };

  const totalPages = data ? Math.ceil(data.count / filters.limit) : 0;

  return (
    <DashboardLayout>
      <div className="min-h-screen bg-background p-6">
        <div className="max-w-7xl mx-auto space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-2xl font-bold text-foreground">
                User Subscriptions Management
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Header with Export Button */}
              <div className="flex justify-between items-center">
                <div className="text-sm text-muted-foreground">
                  {data && `Total ${data.count} users`}
                </div>
                <Button 
                  onClick={exportToCSV} 
                  variant="outline" 
                  className="flex items-center gap-2"
                  disabled={exportLoading}
                >
                  <Download className="w-4 h-4" />
                  {exportLoading ? "Exporting..." : "Export All CSV"}
                </Button>
              </div>

              {/* Filters */}
              <div className="grid grid-cols-1 md:grid-cols-6 gap-4 items-end">
                <div className="md:col-span-2">
                  <label className="text-sm font-medium text-foreground mb-2 block">
                    Search by Email
                  </label>
                  <div className="flex gap-2">
                    <Input
                      placeholder="Enter email address..."
                      value={filters.email}
                      onChange={(e) => setFilters(prev => ({ ...prev, email: e.target.value }))}
                      className="flex-1"
                    />
                    <Button onClick={handleSearch} size="icon">
                      <Search className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
                
                <div>
                  <label className="text-sm font-medium text-foreground mb-2 block">
                    Status Filter
                  </label>
                  <Select 
                    value={filters.status} 
                    onValueChange={(value) => setFilters(prev => ({ ...prev, status: value, page: 0 }))}
                  >
                    <SelectTrigger className="w-full">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all_statuses">All Statuses</SelectItem>
                      <SelectItem value="active">Active</SelectItem>
                      <SelectItem value="canceled">Canceled</SelectItem>
                      <SelectItem value="pending_initial_payment">Pending Payment</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <label className="text-sm font-medium text-foreground mb-2 block">
                    Order By
                  </label>
                  <Select 
                    value={filters.order_by} 
                    onValueChange={(value) => setFilters(prev => ({ ...prev, order_by: value, page: 0 }))}
                  >
                    <SelectTrigger className="w-full">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="user_create_date">Create Date</SelectItem>
                      <SelectItem value="first_name">First Name</SelectItem>
                      <SelectItem value="last_name">Last Name</SelectItem>
                      <SelectItem value="email">Email</SelectItem>
                      <SelectItem value="subscription_date">Subscription Date</SelectItem>
                      <SelectItem value="status">Status</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <label className="text-sm font-medium text-foreground mb-2 block">
                    Order Direction
                  </label>
                  <Select 
                    value={filters.order_dir} 
                    onValueChange={(value) => setFilters(prev => ({ ...prev, order_dir: value, page: 0 }))}
                  >
                    <SelectTrigger className="w-full">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="desc">Descending</SelectItem>
                      <SelectItem value="asc">Ascending</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <label className="text-sm font-medium text-foreground mb-2 block">
                    Per Page
                  </label>
                  <Select 
                    value={filters.limit.toString()} 
                    onValueChange={(value) => setFilters(prev => ({ ...prev, limit: parseInt(value), page: 0 }))}
                  >
                    <SelectTrigger className="w-full">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="25">25</SelectItem>
                      <SelectItem value="50">50</SelectItem>
                      <SelectItem value="100">100</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              {/* Results Summary */}
              <div className="text-sm text-muted-foreground">
                Showing {data ? data.offset + 1 : 0} to {data ? Math.min(data.offset + data.limit, data.count) : 0} of {data ? data.count : 0} users
              </div>

              {/* Table */}
              <div className="border rounded-lg overflow-hidden">
                <Table>
                  <TableHeader>
                    <TableRow className="bg-muted/50">
                      <TableHead className="font-semibold">First Name</TableHead>
                      <TableHead className="font-semibold">Last Name</TableHead>
                      <TableHead className="font-semibold">Email</TableHead>
                      <TableHead className="font-semibold">Create Date</TableHead>
                      <TableHead className="font-semibold">Subscription Date</TableHead>
                      <TableHead className="font-semibold">Status</TableHead>
                      <TableHead className="font-semibold text-center">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {loading ? (
                      <TableRow>
                        <TableCell colSpan={7} className="text-center py-8">
                          <div className="flex items-center justify-center">
                            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-brand-primary"></div>
                            <span className="ml-2">Loading...</span>
                          </div>
                        </TableCell>
                      </TableRow>
                    ) : data?.results.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={7} className="text-center py-8 text-muted-foreground">
                          No users found matching your criteria
                        </TableCell>
                      </TableRow>
                    ) : (
                      data?.results.map((user, index) => (
                        <TableRow key={index} className="hover:bg-muted/30">
                          <TableCell className="font-medium">{user.first_name}</TableCell>
                          <TableCell className="font-medium">{user.last_name}</TableCell>
                          <TableCell>{user.email}</TableCell>
                          <TableCell>{formatDate(user.create_date)}</TableCell>
                          <TableCell>{formatDate(user.subscription_date)}</TableCell>
                          <TableCell>{getStatusBadge(user.status)}</TableCell>
                          <TableCell className="text-center">
                            <Dialog>
                              <DialogTrigger asChild>
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  onClick={() => setSelectedUser(user)}
                                  className="hover:bg-foreground hover:text-background"
                                >
                                  <Eye className="w-4 h-4" />
                                </Button>
                              </DialogTrigger>
                              <DialogContent className="max-w-2xl">
                                <DialogHeader>
                                  <DialogTitle>User Subscription Details</DialogTitle>
                                </DialogHeader>
                                {selectedUser && (
                                  <div className="space-y-4">
                                    <div className="grid grid-cols-2 gap-4">
                                      <div>
                                        <label className="text-sm font-medium text-muted-foreground">Full Name</label>
                                        <p className="text-foreground">{selectedUser.first_name} {selectedUser.last_name}</p>
                                      </div>
                                      <div>
                                        <label className="text-sm font-medium text-muted-foreground">Email</label>
                                        <p className="text-foreground">{selectedUser.email}</p>
                                      </div>
                                      <div>
                                        <label className="text-sm font-medium text-muted-foreground">Account Created</label>
                                        <p className="text-foreground">{formatDate(selectedUser.create_date)}</p>
                                      </div>
                                      <div>
                                        <label className="text-sm font-medium text-muted-foreground">Subscription Date</label>
                                        <p className="text-foreground">{formatDate(selectedUser.subscription_date)}</p>
                                      </div>
                                      <div>
                                        <label className="text-sm font-medium text-muted-foreground">Status</label>
                                        <div className="mt-1">{getStatusBadge(selectedUser.status)}</div>
                                      </div>
                                      <div>
                                        <label className="text-sm font-medium text-muted-foreground">Payment Method</label>
                                        <p className="text-foreground">{selectedUser.payment_method_type || "N/A"}</p>
                                      </div>
                                      <div>
                                        <label className="text-sm font-medium text-muted-foreground">Next Billing</label>
                                        <p className="text-foreground">{formatDate(selectedUser.next_billing_at)}</p>
                                      </div>
                                      <div>
                                        <label className="text-sm font-medium text-muted-foreground">Last Order ID</label>
                                        <p className="text-foreground font-mono text-xs">{selectedUser.last_order_id || "N/A"}</p>
                                      </div>
                                      <div>
                                        <label className="text-sm font-medium text-muted-foreground">Last Login IP</label>
                                        <p className="text-foreground font-mono text-xs">{selectedUser.last_login_ip || "N/A"}</p>
                                      </div>
                                       <div>
                                         <label className="text-sm font-medium text-muted-foreground">Last Seen</label>
                                         <p className="text-foreground">{formatDate(selectedUser.last_seen_at)}</p>
                                       </div>
                                       <div>
                                         <label className="text-sm font-medium text-muted-foreground">Source</label>
                                         <p className="text-foreground">{selectedUser.source || "N/A"}</p>
                                       </div>
                                     </div>
                                    
                                    {/* Location Information */}
                                    <div>
                                      <h3 className="text-lg font-semibold text-foreground mb-2">Location Information</h3>
                                      <div className="grid grid-cols-2 gap-4">
                                        <div>
                                          <label className="text-sm font-medium text-muted-foreground">Country</label>
                                          <p className="text-foreground">{selectedUser.geo_country || "N/A"}</p>
                                        </div>
                                        <div>
                                          <label className="text-sm font-medium text-muted-foreground">Region</label>
                                          <p className="text-foreground">{selectedUser.geo_region || "N/A"}</p>
                                        </div>
                                        <div>
                                          <label className="text-sm font-medium text-muted-foreground">City</label>
                                          <p className="text-foreground">{selectedUser.geo_city || "N/A"}</p>
                                        </div>
                                        <div>
                                          <label className="text-sm font-medium text-muted-foreground">Coordinates</label>
                                          <p className="text-foreground font-mono text-xs">
                                            {selectedUser.geo_latitude && selectedUser.geo_longitude 
                                              ? `${selectedUser.geo_latitude}, ${selectedUser.geo_longitude}`
                                              : "N/A"
                                            }
                                          </p>
                                        </div>
                                      </div>
                                    </div>

                                    {selectedUser.payment_method_id && (
                                      <div>
                                        <label className="text-sm font-medium text-muted-foreground">Payment Method ID</label>
                                        <p className="text-foreground font-mono text-xs bg-muted p-2 rounded">{selectedUser.payment_method_id}</p>
                                      </div>
                                    )}
                                  </div>
                                )}
                              </DialogContent>
                            </Dialog>
                          </TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </div>

              {/* Pagination */}
              {data && totalPages > 1 && (
                <div className="flex items-center justify-between">
                  <div className="text-sm text-muted-foreground">
                    Page {filters.page + 1} of {totalPages}
                  </div>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handlePageChange(filters.page - 1)}
                      disabled={filters.page === 0}
                    >
                      <ChevronLeft className="w-4 h-4 mr-1" />
                      Previous
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handlePageChange(filters.page + 1)}
                      disabled={filters.page >= totalPages - 1}
                    >
                      Next
                      <ChevronRight className="w-4 h-4 ml-1" />
                    </Button>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default UserSubscriptions;