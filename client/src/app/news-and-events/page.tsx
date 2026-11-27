import EventCard from "@/components/main/EventCard";
import NewsCard from "@/components/main/NewsCard";

export default function NewsAndEventsPage() {
  return (
    <main className="space-y-3 p-6">
      <NewsCard />
      <EventCard />
    </main>
  );
}
