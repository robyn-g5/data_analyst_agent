import { useQuery, useQueryClient } from "@tanstack/react-query";
import { fetchMessages } from "@/lib/api";

export function useChatMessages() {
  return useQuery({
    queryKey: ["chatMessages"],
    queryFn: () => fetchMessages(),
    refetchInterval: 3000,
  });
}

export function useInvalidateChat() {
  const queryClient = useQueryClient();
  return () => {
    queryClient.invalidateQueries({ queryKey: ["chatMessages"] });
    queryClient.invalidateQueries({ queryKey: ["runs"] });
  };
}
