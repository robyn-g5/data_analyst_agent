import { useQuery, useQueryClient } from "@tanstack/react-query";
import { fetchRunStatus } from "@/lib/api";
import { isTerminal } from "@/lib/status";

export function useRunStatus(runId: string | null) {
  const queryClient = useQueryClient();

  return useQuery({
    queryKey: ["runStatus", runId],
    queryFn: () => fetchRunStatus(runId!),
    enabled: !!runId,
    refetchInterval: (query) => {
      const data = query.state.data;
      if (!data || !isTerminal(data.status)) return 2000;
      queryClient.invalidateQueries({ queryKey: ["runs"] });
      queryClient.invalidateQueries({ queryKey: ["runDetail", runId] });
      return false;
    },
  });
}
