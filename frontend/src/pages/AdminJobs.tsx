import { useState, useEffect } from "react";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { getJobs } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { format } from "date-fns";

interface Job {
  id: number;
  pipeline_type: string;
  status: string;
  start_time: string;
  end_time: string;
  create_date: string;
  update_date: string;
}

const AdminJobs = () => {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalJobs, setTotalJobs] = useState(0);
  const itemsPerPage = 50;

  const fetchJobs = async (page: number) => {
    setLoading(true);
    try {
      const offset = (page - 1) * itemsPerPage;
      const data = await getJobs({
        limit: itemsPerPage,
        offset,
        order_by: 'start_time',
        order_dir: 'desc',
      });
      
      setJobs(data || []);
      setTotalJobs(data?.length || 0);
    } catch (error) {
      console.error("Error fetching jobs:", error);
      setJobs([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs(currentPage);
  }, [currentPage]);

  const formatDateTime = (dateString: string) => {
    if (!dateString) return "-";
    try {
      return format(new Date(dateString), "MMM dd, yyyy HH:mm:ss");
    } catch {
      return dateString;
    }
  };

  const getStatusBadge = (status: string) => {
    const statusColors: Record<string, "default" | "secondary" | "destructive" | "outline"> = {
      success: "default",
      running: "secondary",
      failed: "destructive",
      pending: "outline",
    };
    
    return (
      <Badge variant={statusColors[status.toLowerCase()] || "secondary"}>
        {status}
      </Badge>
    );
  };

  const totalPages = Math.ceil(totalJobs / itemsPerPage);
  const hasNextPage = currentPage < totalPages;
  const hasPreviousPage = currentPage > 1;

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Pipeline Jobs</h1>
          <p className="text-muted-foreground mt-2">
            Monitor and manage all pipeline job executions
          </p>
        </div>

        <div className="bg-card border border-border rounded-lg shadow-sm">
          {loading ? (
            <div className="p-8 text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-primary mx-auto"></div>
              <p className="text-muted-foreground mt-4">Loading jobs...</p>
            </div>
          ) : jobs.length === 0 ? (
            <div className="p-8 text-center">
              <p className="text-muted-foreground">No jobs found</p>
            </div>
          ) : (
            <>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Pipeline Type</TableHead>
                    <TableHead>Start Time</TableHead>
                    <TableHead>End Time</TableHead>
                    <TableHead>Status</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {jobs.map((job) => (
                    <TableRow key={job.id}>
                      <TableCell className="font-medium">
                        {job.pipeline_type}
                      </TableCell>
                      <TableCell>{formatDateTime(job.start_time)}</TableCell>
                      <TableCell>{formatDateTime(job.end_time)}</TableCell>
                      <TableCell>{getStatusBadge(job.status)}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>

              {totalPages > 1 && (
                <div className="border-t border-border p-4">
                  <Pagination>
                    <PaginationContent>
                      <PaginationItem>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                          disabled={!hasPreviousPage}
                          className="gap-1"
                        >
                          <ChevronLeft className="h-4 w-4" />
                          Previous
                        </Button>
                      </PaginationItem>

                      <PaginationItem>
                        <span className="text-sm text-muted-foreground px-4">
                          Page {currentPage} of {totalPages}
                        </span>
                      </PaginationItem>

                      <PaginationItem>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => setCurrentPage(p => p + 1)}
                          disabled={!hasNextPage}
                          className="gap-1"
                        >
                          Next
                          <ChevronRight className="h-4 w-4" />
                        </Button>
                      </PaginationItem>
                    </PaginationContent>
                  </Pagination>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
};

export default AdminJobs;