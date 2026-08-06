import { useQuery } from "@tanstack/react-query";
import { fetchRunDetail } from "@/lib/api";
import { isTerminal } from "@/lib/status";
import type { RunSummary } from "@/lib/types";

export function useRunDetail(run: RunSummary | null) {
  return useQuery({
    queryKey: ["runDetail", run?.id],
    queryFn: () => fetchRunDetail(run!.id),
    enabled: !!run && isTerminal(run.status),
  });
}
